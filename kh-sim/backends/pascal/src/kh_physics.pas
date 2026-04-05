unit kh_physics;
{ KH instability physics kernel — Pascal (Free Pascal 3.2+)
  Physics : 2D incompressible Navier-Stokes, vorticity-streamfunction form.
  Numerics : pseudo-spectral (Cooley-Tukey radix-2), RK4.
  Reference: kh-sim/shared/physics/KH-PHYSICS.md
  Canonical: kh-sim/shared/physics/kh_physics.py
}
{$mode objfpc}{$H+}

interface

uses Math, SysUtils, DateUtils;

{ ── Complex arithmetic ───────────────────────────────────────────────────── }
type
  TComplex    = record re, im: Double; end;
  TComplexArr = array of TComplex;
  TRealArr    = array of Double;

operator + (const a, b: TComplex): TComplex; inline;
operator - (const a, b: TComplex): TComplex; inline;
operator * (const a, b: TComplex): TComplex; inline;
operator * (const a: Double; const b: TComplex): TComplex; inline;
operator * (const a: TComplex; const b: Double): TComplex; inline;
operator / (const a: TComplex; const b: Double): TComplex; inline;

function CmplxOf(re, im: Double): TComplex; inline;
function CmplxFromReal(const r: TRealArr; n: Integer): TComplexArr;
function RealPart(const c: TComplexArr; n: Integer): TRealArr;

{ ── Simulation API ───────────────────────────────────────────────────────── }
type
  TSimRequest = record
    nx, ny, steps, mode: Integer;
    lx, ly, dt, re, u0, amp: Double;
  end;

  TSimResult = record
    u, v, omega, psi: TRealArr;
    ke, enstrophy, max_vort, div_rms, compute_ms: Double;
  end;

function Simulate(const req: TSimRequest): TSimResult;

implementation

{ ── Operator implementations ─────────────────────────────────────────────── }
operator + (const a, b: TComplex): TComplex;
begin Result.re := a.re + b.re; Result.im := a.im + b.im; end;

operator - (const a, b: TComplex): TComplex;
begin Result.re := a.re - b.re; Result.im := a.im - b.im; end;

operator * (const a, b: TComplex): TComplex;
begin
  Result.re := a.re*b.re - a.im*b.im;
  Result.im := a.re*b.im + a.im*b.re;
end;

operator * (const a: Double; const b: TComplex): TComplex;
begin Result.re := a*b.re; Result.im := a*b.im; end;

operator * (const a: TComplex; const b: Double): TComplex;
begin Result.re := a.re*b; Result.im := a.im*b; end;

operator / (const a: TComplex; const b: Double): TComplex;
begin Result.re := a.re/b; Result.im := a.im/b; end;

function CmplxOf(re, im: Double): TComplex;
begin Result.re := re; Result.im := im; end;

function CmplxFromReal(const r: TRealArr; n: Integer): TComplexArr;
var i: Integer;
begin
  SetLength(Result, n);
  for i := 0 to n-1 do begin Result[i].re := r[i]; Result[i].im := 0.0; end;
end;

function RealPart(const c: TComplexArr; n: Integer): TRealArr;
var i: Integer;
begin
  SetLength(Result, n);
  for i := 0 to n-1 do Result[i] := c[i].re;
end;

{ ── 1D in-place Cooley-Tukey FFT (radix-2, DIT) ─────────────────────────── }
{ n must be a power of 2. inverse=True applies 1/n normalisation.             }
procedure FFT1D(var a: TComplexArr; n: Integer; inverse: Boolean);
var
  i, j, bit, len, k: Integer;
  ang: Double;
  wlen, w, u, v: TComplex;
begin
  { bit-reversal permutation }
  j := 0;
  for i := 1 to n-1 do begin
    bit := n shr 1;
    while (j and bit) <> 0 do begin
      j := j xor bit;
      bit := bit shr 1;
    end;
    j := j xor bit;
    if i < j then begin u := a[i]; a[i] := a[j]; a[j] := u; end;
  end;
  { butterfly stages }
  len := 2;
  while len <= n do begin
    ang := 2.0*Pi / len;
    if inverse then ang := -ang;
    wlen := CmplxOf(Cos(ang), Sin(ang));
    i := 0;
    while i < n do begin
      w := CmplxOf(1.0, 0.0);
      for k := 0 to (len shr 1)-1 do begin
        u := a[i+k];
        v := a[i+k+(len shr 1)] * w;
        a[i+k]              := u + v;
        a[i+k+(len shr 1)] := u - v;
        w := w * wlen;
      end;
      i := i + len;
    end;
    len := len shl 1;
  end;
  { normalise inverse }
  if inverse then
    for i := 0 to n-1 do a[i] := a[i] / n;
end;

{ ── 2D FFT: row-then-column (row-major a[i*ny+j]) ───────────────────────── }
procedure FFT2D(var a: TComplexArr; nx, ny: Integer; inverse: Boolean);
var
  i, j: Integer;
  row, col: TComplexArr;
begin
  SetLength(row, ny);
  SetLength(col, nx);
  { FFT along y-axis (rows of length ny) }
  for i := 0 to nx-1 do begin
    for j := 0 to ny-1 do row[j] := a[i*ny+j];
    FFT1D(row, ny, inverse);
    for j := 0 to ny-1 do a[i*ny+j] := row[j];
  end;
  { FFT along x-axis (columns of length nx) }
  for j := 0 to ny-1 do begin
    for i := 0 to nx-1 do col[i] := a[i*ny+j];
    FFT1D(col, nx, inverse);
    for i := 0 to nx-1 do a[i*ny+j] := col[i];
  end;
end;

{ ── Angular wavenumber meshgrid, row-major ───────────────────────────────── }
{ kx[i*ny+j] = 2π*fftfreq(i,nx)/dx,  ky[i*ny+j] = 2π*fftfreq(j,ny)/dy     }
procedure MakeWavenumbers(nx, ny: Integer; dx, dy: Double;
  out kx, ky: TRealArr);
var i, j, fi, fj: Integer;
begin
  SetLength(kx, nx*ny);
  SetLength(ky, nx*ny);
  for i := 0 to nx-1 do begin
    if i <= nx div 2 then fi := i else fi := i - nx;
    for j := 0 to ny-1 do kx[i*ny+j] := 2.0*Pi*fi / (nx*dx);
  end;
  for j := 0 to ny-1 do begin
    if j <= ny div 2 then fj := j else fj := j - ny;
    for i := 0 to nx-1 do ky[i*ny+j] := 2.0*Pi*fj / (ny*dy);
  end;
end;

{ ── Initial conditions: tanh shear + sinusoidal perturbation ─────────────── }
procedure InitConds(nx, ny: Integer; lx, ly, u0, delta, amp: Double;
  mode: Integer; out omega: TRealArr);
var i, j: Integer;
    dx, dy, x, y, z, pert: Double;
begin
  SetLength(omega, nx*ny);
  dx := lx / nx;  dy := ly / ny;
  for i := 0 to nx-1 do begin
    x    := i * dx;
    pert := amp * (2.0*Pi*mode/lx) * Cos(2.0*Pi*mode*x/lx);
    for j := 0 to ny-1 do begin
      y := j * dy;
      z := (y - ly*0.5) / delta;
      omega[i*ny+j] := (u0/delta) / (Cosh(z)*Cosh(z)) + pert;
    end;
  end;
end;

{ ── Spectral Poisson: psi_hat = omega_hat / k², zero mode = 0 ───────────── }
procedure SolvePoisson(const oh: TComplexArr; const kx, ky: TRealArr;
  nx, ny: Integer; out ph: TComplexArr);
var i, j, idx: Integer; k2: Double;
begin
  SetLength(ph, nx*ny);
  for i := 0 to nx-1 do
    for j := 0 to ny-1 do begin
      idx := i*ny+j;
      if (i=0) and (j=0) then
        ph[idx] := CmplxOf(0.0, 0.0)
      else begin
        k2 := kx[idx]*kx[idx] + ky[idx]*ky[idx];
        ph[idx] := oh[idx] / k2;
      end;
    end;
end;

{ ── Velocity from streamfunction ─────────────────────────────────────────── }
{ u_hat = i·ky·ψ̂  →  re=-ky·ψ̂.im, im=+ky·ψ̂.re                           }
{ v_hat = -i·kx·ψ̂ →  re=+kx·ψ̂.im, im=-kx·ψ̂.re                           }
procedure VelFromPsi(const ph: TComplexArr; const kx, ky: TRealArr;
  nx, ny: Integer; out u, v: TRealArr);
var i, j, idx, n: Integer;
    uh, vh: TComplexArr;
begin
  n := nx*ny;
  SetLength(uh, n); SetLength(vh, n);
  for i := 0 to nx-1 do
    for j := 0 to ny-1 do begin
      idx := i*ny+j;
      uh[idx] := CmplxOf(-ky[idx]*ph[idx].im,  ky[idx]*ph[idx].re);
      vh[idx] := CmplxOf( kx[idx]*ph[idx].im, -kx[idx]*ph[idx].re);
    end;
  FFT2D(uh, nx, ny, True);
  FFT2D(vh, nx, ny, True);
  u := RealPart(uh, n);
  v := RealPart(vh, n);
end;

{ ── Vorticity RHS: -u·∂ω/∂x - v·∂ω/∂y + ν·∇²ω ────────────────────────── }
procedure VortRHS(const omega, uin, vin, kx, ky: TRealArr;
  nx, ny: Integer; nu: Double; out rhs: TRealArr);
var
  i, j, idx, n: Integer;
  k2: Double;
  oh, dxs, dys, laps: TComplexArr;
  dox, doy, lap: TRealArr;
begin
  n := nx*ny;
  oh := CmplxFromReal(omega, n);
  FFT2D(oh, nx, ny, False);
  SetLength(dxs, n); SetLength(dys, n); SetLength(laps, n);
  for i := 0 to nx-1 do
    for j := 0 to ny-1 do begin
      idx := i*ny+j;
      k2  := kx[idx]*kx[idx] + ky[idx]*ky[idx];
      { i·kx·ω̂ }  dxs[idx]  := CmplxOf(-kx[idx]*oh[idx].im,  kx[idx]*oh[idx].re);
      { i·ky·ω̂ }  dys[idx]  := CmplxOf(-ky[idx]*oh[idx].im,  ky[idx]*oh[idx].re);
      { -k²·ω̂  }  laps[idx] := oh[idx] * (-k2);
    end;
  FFT2D(dxs,  nx, ny, True);  dox := RealPart(dxs,  n);
  FFT2D(dys,  nx, ny, True);  doy := RealPart(dys,  n);
  FFT2D(laps, nx, ny, True);  lap := RealPart(laps, n);
  SetLength(rhs, n);
  for idx := 0 to n-1 do
    rhs[idx] := -uin[idx]*dox[idx] - vin[idx]*doy[idx] + nu*lap[idx];
end;

{ ── RK4 time step ────────────────────────────────────────────────────────── }
procedure RK4Step(const omega, kx, ky: TRealArr;
  nx, ny: Integer; nu, dt: Double; out omega_out: TRealArr);
var
  n, idx: Integer;
  k1, k2, k3, k4, tmp, u, v: TRealArr;
  oh, ph: TComplexArr;
begin
  n := nx*ny;
  SetLength(tmp, n);

  oh := CmplxFromReal(omega, n); FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  VelFromPsi(ph, kx, ky, nx, ny, u, v);
  VortRHS(omega, u, v, kx, ky, nx, ny, nu, k1);

  for idx := 0 to n-1 do tmp[idx] := omega[idx] + 0.5*dt*k1[idx];
  oh := CmplxFromReal(tmp, n); FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  VelFromPsi(ph, kx, ky, nx, ny, u, v);
  VortRHS(tmp, u, v, kx, ky, nx, ny, nu, k2);

  for idx := 0 to n-1 do tmp[idx] := omega[idx] + 0.5*dt*k2[idx];
  oh := CmplxFromReal(tmp, n); FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  VelFromPsi(ph, kx, ky, nx, ny, u, v);
  VortRHS(tmp, u, v, kx, ky, nx, ny, nu, k3);

  for idx := 0 to n-1 do tmp[idx] := omega[idx] + dt*k3[idx];
  oh := CmplxFromReal(tmp, n); FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  VelFromPsi(ph, kx, ky, nx, ny, u, v);
  VortRHS(tmp, u, v, kx, ky, nx, ny, nu, k4);

  SetLength(omega_out, n);
  for idx := 0 to n-1 do
    omega_out[idx] := omega[idx] + (dt/6.0)*(k1[idx] + 2.0*k2[idx] + 2.0*k3[idx] + k4[idx]);
end;

{ ── Main simulate entry point ────────────────────────────────────────────── }
function Simulate(const req: TSimRequest): TSimResult;
var
  nx, ny, n, s, idx: Integer;
  lx, ly, dt, nu, delta, dx, dy: Double;
  omega, omega_next, kx, ky, u, v, psi_r: TRealArr;
  oh, ph, ph2, uh, vh, div_s: TComplexArr;
  ke_sum, ens_sum, max_w, div_sum, n_inv: Double;
  t_start: TDateTime;
begin
  nx := req.nx;  ny := req.ny;  n := nx*ny;
  lx := req.lx;  ly := req.ly;  dt := req.dt;
  nu    := req.u0 / req.re;
  delta := 0.05 * ly;
  dx    := lx / nx;
  dy    := ly / ny;

  MakeWavenumbers(nx, ny, dx, dy, kx, ky);
  InitConds(nx, ny, lx, ly, req.u0, delta, req.amp, req.mode, omega);

  t_start := Now;
  for s := 1 to req.steps do begin
    RK4Step(omega, kx, ky, nx, ny, nu, dt, omega_next);
    omega := omega_next;
  end;
  Result.compute_ms := MilliSecondsBetween(Now, t_start);

  { final psi via ifft(solve_poisson(fft(omega))) }
  oh := CmplxFromReal(omega, n);  FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  SetLength(ph2, n);
  for idx := 0 to n-1 do ph2[idx] := ph[idx];
  FFT2D(ph2, nx, ny, True);
  psi_r := RealPart(ph2, n);

  { re-solve ph for velocity (ph was consumed by ifft above) }
  oh := CmplxFromReal(omega, n);  FFT2D(oh, nx, ny, False);
  SolvePoisson(oh, kx, ky, nx, ny, ph);
  VelFromPsi(ph, kx, ky, nx, ny, u, v);

  { diagnostics }
  n_inv := 1.0 / n;
  ke_sum := 0.0;  ens_sum := 0.0;  max_w := 0.0;
  for idx := 0 to n-1 do begin
    ke_sum  := ke_sum  + 0.5*(u[idx]*u[idx] + v[idx]*v[idx]);
    ens_sum := ens_sum + 0.5*omega[idx]*omega[idx];
    if Abs(omega[idx]) > max_w then max_w := Abs(omega[idx]);
  end;

  { divergence rms: div = i·kx·û + i·ky·v̂ }
  uh := CmplxFromReal(u, n);  FFT2D(uh, nx, ny, False);
  vh := CmplxFromReal(v, n);  FFT2D(vh, nx, ny, False);
  SetLength(div_s, n);
  for idx := 0 to n-1 do
    div_s[idx] := CmplxOf(
      -kx[idx]*uh[idx].im - ky[idx]*vh[idx].im,
       kx[idx]*uh[idx].re + ky[idx]*vh[idx].re);
  FFT2D(div_s, nx, ny, True);
  div_sum := 0.0;
  for idx := 0 to n-1 do div_sum := div_sum + div_s[idx].re * div_s[idx].re;

  Result.u          := u;
  Result.v          := v;
  Result.omega      := omega;
  Result.psi        := psi_r;
  Result.ke         := ke_sum  * n_inv;
  Result.enstrophy  := ens_sum * n_inv;
  Result.max_vort   := max_w;
  Result.div_rms    := Sqrt(div_sum * n_inv);
end;

end.
