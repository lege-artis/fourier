program kh_validate;
{ KH-007 Pascal validation — compares against Python/NumPy reference values.
  Error always reported in scientific notation (%.3e) — never "0.00%".
  Exit code 0 = all passed, 1 = any failure.
}
{$mode objfpc}{$H+}

uses
  SysUtils, Math, Classes, fpjson, jsonparser,
  kh_physics;

{ ── Reference loader ─────────────────────────────────────────────────────── }
type
  TRef = record
    ke, enstrophy, max_vort, div_rms: Double;
    nx, ny, steps: Integer;
  end;

function LoadRef(const fname: string): TRef;
var
  sl:   TStringList;
  jo:   TJSONObject;
  diag: TJSONObject;
  jd:   TJSONData;
begin
  sl := TStringList.Create;
  try
    sl.LoadFromFile(fname);
    jo := GetJSON(sl.Text) as TJSONObject;
    try
      { Grid size / steps — self-calibrate against whatever the reference used }
      jd := jo.Find('grid_nx');
      if Assigned(jd) then Result.nx := jd.AsInteger else Result.nx := 64;
      jd := jo.Find('grid_ny');
      if Assigned(jd) then Result.ny := jd.AsInteger else Result.ny := 32;
      jd := jo.Find('steps_completed');
      if Assigned(jd) then Result.steps := jd.AsInteger else Result.steps := 100;

      { Reference JSON nests diagnostics under "diagnostics" sub-object }
      diag := jo.Find('diagnostics') as TJSONObject;
      if not Assigned(diag) then
        raise Exception.Create('JSON missing "diagnostics" key');
      Result.ke        := diag.Find('kinetic_energy').AsFloat;
      Result.enstrophy := diag.Find('enstrophy').AsFloat;
      Result.max_vort  := diag.Find('max_vorticity').AsFloat;
      Result.div_rms   := diag.Find('divergence_rms').AsFloat;
    finally
      jo.Free;
    end;
  finally
    sl.Free;
  end;
end;

{ ── Check helper ─────────────────────────────────────────────────────────── }
{ err always displayed in scientific notation — no "0.00%" masking.           }
const
  KE_TOL  = 0.05;    { 5% relative tolerance for KE / enstrophy }
  DIV_TOL = 1.0e-10; { absolute threshold for divergence_rms    }

var
  g_pass: Boolean = True;

procedure Check(const name: string; got, refval, tol: Double);
var
  err: Double;
begin
  if Abs(refval) > 1e-30 then
    err := Abs(got - refval) / Abs(refval)
  else
    err := Abs(got - refval);
  { Always show true relative error in scientific notation }
  Write(Format('%-15s : got=%.6f  ref=%.6f  err=%.3e%%',
               [name, got, refval, err*100]));
  if err > tol then begin
    WriteLn(Format('  FAIL (tol=%.0f%%)', [tol*100]));
    g_pass := False;
  end else
    WriteLn;
end;

procedure CheckDiv(got, refval: Double);
begin
  Write(Format('%-15s : got=%.3e   ref=%.3e',
               ['divergence_rms', got, refval]));
  if got > DIV_TOL then begin
    WriteLn(Format('  FAIL (>%.0e)', [DIV_TOL]));
    g_pass := False;
  end else
    WriteLn('  OK');
end;

{ ── Main ─────────────────────────────────────────────────────────────────── }
var
  ref:       TRef;
  ref_nx:    Integer;
  ref_ny:    Integer;
  ref_steps: Integer;
  req: TSimRequest;
  res: TSimResult;
begin
  if ParamCount < 1 then begin
    WriteLn('Usage: kh-sim-pascal-validate <kh_reference_output.json>');
    Halt(1);
  end;

  ref       := LoadRef(ParamStr(1));
  ref_nx    := ref.nx;
  ref_ny    := ref.ny;
  ref_steps := ref.steps;

  with req do begin
    { Parameters MUST match the reference JSON generation run (Python defaults):
      lx=1.0, ly=0.5, dt=0.001, steps=100, Re=1000, u0=1, amp=0.01, mode=2.
      nx/ny are read from the JSON so the test is self-calibrating on grid. }
    nx := ref_nx;  ny := ref_ny;
    lx := 1.0;     ly := 0.5;
    dt := 0.001;   steps := ref_steps;
    re := 1000.0;  u0 := 1.0;
    amp := 0.01;   mode := 2;
  end;

  WriteLn('--- Pascal vs Python reference ---');
  res := Simulate(req);

  Check('kinetic_energy',  res.ke,        ref.ke,       KE_TOL);
  Check('enstrophy',       res.enstrophy,  ref.enstrophy, KE_TOL);
  Check('max_vorticity',   res.max_vort,   ref.max_vort,  KE_TOL);
  CheckDiv(res.div_rms, ref.div_rms);
  WriteLn(Format('%-15s : %.3e ms', ['compute_ms', res.compute_ms]));
  WriteLn;

  if g_pass then
    WriteLn('All tests PASSED')
  else begin
    WriteLn('TESTS FAILED');
    Halt(1);
  end;
end.
