! kh_physics.f90 — KH instability physics kernel (Fortran 2008)
!
! Physics: 2D incompressible Navier-Stokes, vorticity-streamfunction form.
! Numerics: pseudo-spectral (Cooley-Tukey in-place radix-2 FFT), RK4.
!
! Exported via iso_c_binding for C++ HTTP shim (kh_shim.cpp).
!
! Reference: kh-sim/shared/physics/KH-PHYSICS.md
! Canonical:  kh-sim/shared/physics/kh_physics.py

module kh_physics
  use iso_c_binding, only: c_double, c_int, c_ptr, c_f_pointer, c_null_ptr, c_associated
  implicit none
  private

  real(c_double), parameter :: PI = 3.14159265358979323846_c_double

  ! ── Complex type alias ──────────────────────────────────────────────────────
  ! Fortran intrinsic complex(8) == complex(kind=c_double)

  public :: kh_simulate_c

contains

  ! ── 1D in-place Cooley-Tukey FFT (radix-2, DIT) ────────────────────────────
  ! n must be a power of 2.
  ! inverse=.true. applies 1/n normalisation.

  subroutine fft1d(a, n, inverse)
    integer,     intent(in)    :: n
    complex(8),  intent(inout) :: a(0:n-1)
    logical,     intent(in)    :: inverse

    integer     :: i, j, bit, len, k
    complex(8)  :: wlen, w, u, v
    real(8)     :: ang

    ! bit-reversal permutation
    j = 0
    do i = 1, n-1
      bit = n / 2
      do while (iand(j, bit) /= 0)
        j = ieor(j, bit)
        bit = bit / 2
      end do
      j = ieor(j, bit)
      if (i < j) then
        u = a(i); a(i) = a(j); a(j) = u
      end if
    end do

    ! butterfly stages
    len = 2
    do while (len <= n)
      ang = 2.0_8 * PI / real(len, 8)
      if (inverse) ang = -ang
      wlen = cmplx(cos(ang), sin(ang), kind=8)
      i = 0
      do while (i < n)
        w = cmplx(1.0_8, 0.0_8, kind=8)
        do k = 0, len/2 - 1
          u = a(i + k)
          v = a(i + k + len/2) * w
          a(i + k)         = u + v
          a(i + k + len/2) = u - v
          w = w * wlen
        end do
        i = i + len
      end do
      len = len * 2
    end do

    ! normalise for inverse
    if (inverse) then
      a = a / real(n, 8)
    end if
  end subroutine fft1d

  ! ── 2D FFT: row-then-column ──────────────────────────────────────────────────
  ! a(0:nx-1, 0:ny-1) in column-major Fortran order.
  ! We process: rows (axis-1, ny elements) then columns (axis-0, nx elements).

  subroutine fft2d(a, nx, ny, inverse)
    integer,    intent(in)    :: nx, ny
    complex(8), intent(inout) :: a(0:nx-1, 0:ny-1)
    logical,    intent(in)    :: inverse
    integer :: i, j
    complex(8) :: row(0:ny-1), col(0:nx-1)

    ! FFT along axis-1 (each row of length ny)
    do i = 0, nx-1
      do j = 0, ny-1; row(j) = a(i,j); end do
      call fft1d(row, ny, inverse)
      do j = 0, ny-1; a(i,j) = row(j); end do
    end do

    ! FFT along axis-0 (each column of length nx)
    do j = 0, ny-1
      do i = 0, nx-1; col(i) = a(i,j); end do
      call fft1d(col, nx, inverse)
      do i = 0, nx-1; a(i,j) = col(i); end do
    end do
  end subroutine fft2d

  ! ── Wavenumbers ───────────────────────────────────────────────────────────────
  ! Returns angular fftfreq: kfreq(i) = 2*PI * i/(n*d)  for i<=n/2
  !                                    = 2*PI*(i-n)/(n*d) for i>n/2

  subroutine make_wavenumbers(nx, ny, dx, dy, kx, ky)
    integer,    intent(in)  :: nx, ny
    real(8),    intent(in)  :: dx, dy
    real(8),    intent(out) :: kx(0:nx-1, 0:ny-1)
    real(8),    intent(out) :: ky(0:nx-1, 0:ny-1)
    integer :: i, j
    real(8) :: kx1(0:nx-1), ky1(0:ny-1)

    do i = 0, nx/2
      kx1(i) = 2.0_8 * PI * real(i,8) / (real(nx,8) * dx)
    end do
    do i = nx/2+1, nx-1
      kx1(i) = 2.0_8 * PI * real(i-nx,8) / (real(nx,8) * dx)
    end do
    do j = 0, ny/2
      ky1(j) = 2.0_8 * PI * real(j,8) / (real(ny,8) * dy)
    end do
    do j = ny/2+1, ny-1
      ky1(j) = 2.0_8 * PI * real(j-ny,8) / (real(ny,8) * dy)
    end do

    do j = 0, ny-1
      do i = 0, nx-1
        kx(i,j) = kx1(i)
        ky(i,j) = ky1(j)
      end do
    end do
  end subroutine make_wavenumbers

  ! ── Initial conditions ────────────────────────────────────────────────────────
  subroutine initial_conditions(nx, ny, lx, ly, u0, delta, amp, mode, omega)
    integer, intent(in)  :: nx, ny, mode
    real(8), intent(in)  :: lx, ly, u0, delta, amp
    real(8), intent(out) :: omega(0:nx-1, 0:ny-1)
    integer :: i, j
    real(8) :: dx, dy, x, y, z, pert_x

    dx = lx / real(nx, 8)
    dy = ly / real(ny, 8)
    do i = 0, nx-1
      x = real(i,8) * dx
      pert_x = amp * (2.0_8*PI*real(mode,8)/lx) * cos(2.0_8*PI*real(mode,8)*x/lx)
      do j = 0, ny-1
        y = real(j,8) * dy
        z = (y - ly/2.0_8) / delta
        omega(i,j) = u0/delta/cosh(z)**2 + pert_x
      end do
    end do
  end subroutine initial_conditions

  ! ── Poisson solve: psi_hat = omega_hat / k^2, zero mode = 0 ─────────────────
  subroutine solve_poisson(omega_hat, kx, ky, nx, ny, psi_hat)
    integer,    intent(in)  :: nx, ny
    complex(8), intent(in)  :: omega_hat(0:nx-1, 0:ny-1)
    real(8),    intent(in)  :: kx(0:nx-1, 0:ny-1), ky(0:nx-1, 0:ny-1)
    complex(8), intent(out) :: psi_hat(0:nx-1, 0:ny-1)
    integer :: i, j
    real(8) :: k2
    do j = 0, ny-1
      do i = 0, nx-1
        if (i == 0 .and. j == 0) then
          psi_hat(0,0) = cmplx(0.0_8, 0.0_8, kind=8)
        else
          k2 = kx(i,j)**2 + ky(i,j)**2
          psi_hat(i,j) = omega_hat(i,j) / k2
        end if
      end do
    end do
  end subroutine solve_poisson

  ! ── Velocity from streamfunction ──────────────────────────────────────────────
  ! u_hat = i*ky*psi_hat,  v_hat = -i*kx*psi_hat
  subroutine velocity_from_psi(psi_hat, kx, ky, nx, ny, u, v)
    integer,    intent(in)  :: nx, ny
    complex(8), intent(in)  :: psi_hat(0:nx-1, 0:ny-1)
    real(8),    intent(in)  :: kx(0:nx-1, 0:ny-1), ky(0:nx-1, 0:ny-1)
    real(8),    intent(out) :: u(0:nx-1, 0:ny-1), v(0:nx-1, 0:ny-1)
    complex(8) :: u_hat(0:nx-1, 0:ny-1), v_hat(0:nx-1, 0:ny-1)
    complex(8), parameter :: I_UNIT = (0.0_8, 1.0_8)
    integer :: i, j

    do j = 0, ny-1
      do i = 0, nx-1
        u_hat(i,j) =  I_UNIT * ky(i,j) * psi_hat(i,j)
        v_hat(i,j) = -I_UNIT * kx(i,j) * psi_hat(i,j)
      end do
    end do
    call fft2d(u_hat, nx, ny, .true.)
    call fft2d(v_hat, nx, ny, .true.)
    u = real(u_hat, kind=8)
    v = real(v_hat, kind=8)
  end subroutine velocity_from_psi

  ! ── Vorticity RHS ─────────────────────────────────────────────────────────────
  subroutine vorticity_rhs(omega, u_in, v_in, nu, kx, ky, nx, ny, rhs)
    integer,    intent(in)  :: nx, ny
    real(8),    intent(in)  :: omega(0:nx-1,0:ny-1)
    real(8),    intent(in)  :: u_in(0:nx-1,0:ny-1), v_in(0:nx-1,0:ny-1)
    real(8),    intent(in)  :: nu, kx(0:nx-1,0:ny-1), ky(0:nx-1,0:ny-1)
    real(8),    intent(out) :: rhs(0:nx-1, 0:ny-1)

    complex(8) :: oh(0:nx-1,0:ny-1), dx_s(0:nx-1,0:ny-1)
    complex(8) :: dy_s(0:nx-1,0:ny-1), lap_s(0:nx-1,0:ny-1)
    real(8)    :: dox(0:nx-1,0:ny-1), doy(0:nx-1,0:ny-1), lap(0:nx-1,0:ny-1)
    complex(8), parameter :: I_UNIT = (0.0_8, 1.0_8)
    integer :: i, j
    real(8) :: k2

    oh = cmplx(omega, 0.0_8, kind=8)
    call fft2d(oh, nx, ny, .false.)

    do j = 0, ny-1
      do i = 0, nx-1
        dx_s(i,j)  = I_UNIT * kx(i,j) * oh(i,j)
        dy_s(i,j)  = I_UNIT * ky(i,j) * oh(i,j)
        k2         = kx(i,j)**2 + ky(i,j)**2
        lap_s(i,j) = -k2 * oh(i,j)
      end do
    end do

    call fft2d(dx_s,  nx, ny, .true.);  dox = real(dx_s,  kind=8)
    call fft2d(dy_s,  nx, ny, .true.);  doy = real(dy_s,  kind=8)
    call fft2d(lap_s, nx, ny, .true.);  lap = real(lap_s, kind=8)

    rhs = -u_in*dox - v_in*doy + nu*lap
  end subroutine vorticity_rhs

  ! ── RK4 step ──────────────────────────────────────────────────────────────────
  subroutine rk4_step(omega, nu, kx, ky, nx, ny, dt, omega_out)
    integer,    intent(in)  :: nx, ny
    real(8),    intent(in)  :: omega(0:nx-1,0:ny-1)
    real(8),    intent(in)  :: nu, dt, kx(0:nx-1,0:ny-1), ky(0:nx-1,0:ny-1)
    real(8),    intent(out) :: omega_out(0:nx-1,0:ny-1)

    real(8) :: k1(0:nx-1,0:ny-1), k2(0:nx-1,0:ny-1)
    real(8) :: k3(0:nx-1,0:ny-1), k4(0:nx-1,0:ny-1)
    real(8) :: tmp(0:nx-1,0:ny-1)
    complex(8) :: wh(0:nx-1,0:ny-1), ph(0:nx-1,0:ny-1)
    real(8)    :: u(0:nx-1,0:ny-1),  v(0:nx-1,0:ny-1)

    ! k1
    wh = cmplx(omega, 0.0_8, kind=8); call fft2d(wh, nx, ny, .false.)
    call solve_poisson(wh, kx, ky, nx, ny, ph)
    call velocity_from_psi(ph, kx, ky, nx, ny, u, v)
    call vorticity_rhs(omega, u, v, nu, kx, ky, nx, ny, k1)

    ! k2
    tmp = omega + 0.5_8*dt*k1
    wh = cmplx(tmp, 0.0_8, kind=8); call fft2d(wh, nx, ny, .false.)
    call solve_poisson(wh, kx, ky, nx, ny, ph)
    call velocity_from_psi(ph, kx, ky, nx, ny, u, v)
    call vorticity_rhs(tmp, u, v, nu, kx, ky, nx, ny, k2)

    ! k3
    tmp = omega + 0.5_8*dt*k2
    wh = cmplx(tmp, 0.0_8, kind=8); call fft2d(wh, nx, ny, .false.)
    call solve_poisson(wh, kx, ky, nx, ny, ph)
    call velocity_from_psi(ph, kx, ky, nx, ny, u, v)
    call vorticity_rhs(tmp, u, v, nu, kx, ky, nx, ny, k3)

    ! k4
    tmp = omega + dt*k3
    wh = cmplx(tmp, 0.0_8, kind=8); call fft2d(wh, nx, ny, .false.)
    call solve_poisson(wh, kx, ky, nx, ny, ph)
    call velocity_from_psi(ph, kx, ky, nx, ny, u, v)
    call vorticity_rhs(tmp, u, v, nu, kx, ky, nx, ny, k4)

    omega_out = omega + (dt/6.0_8)*(k1 + 2.0_8*k2 + 2.0_8*k3 + k4)
  end subroutine rk4_step

  ! ── C-interop entry point ─────────────────────────────────────────────────────
  ! Called from kh_shim.cpp via iso_c_binding.
  ! All arrays passed as flat C double* (row-major from C side).
  !
  ! Fortran stores in column-major; we accept row-major from C and transpose
  ! on entry/exit so physics indexing omega(i_x, j_y) is consistent.

  subroutine kh_simulate_c(        &
      c_nx, c_ny,                  &
      c_lx, c_ly,                  &
      c_dt, c_steps,               &
      c_re, c_u0, c_amp, c_mode,   &
      c_init_omega,                &
      c_u, c_v, c_omega, c_psi,    &
      c_ke, c_enstrophy,           &
      c_max_vort, c_div_rms        &
    ) bind(c, name="kh_simulate_c")

    integer(c_int), value, intent(in)  :: c_nx, c_ny, c_steps, c_mode
    real(c_double), value, intent(in)  :: c_lx, c_ly, c_dt, c_re, c_u0, c_amp
    ! init_omega: pointer to flat array or NULL (use analytic IC)
    type(c_ptr),    value, intent(in)  :: c_init_omega
    real(c_double), intent(out)        :: c_u(0:c_nx*c_ny-1)
    real(c_double), intent(out)        :: c_v(0:c_nx*c_ny-1)
    real(c_double), intent(out)        :: c_omega(0:c_nx*c_ny-1)
    real(c_double), intent(out)        :: c_psi(0:c_nx*c_ny-1)
    real(c_double), intent(out)        :: c_ke, c_enstrophy, c_max_vort, c_div_rms

    integer :: nx, ny, steps, mode, i, j, s
    real(8) :: lx, ly, dt, nu, delta, dx, dy, t
    real(8), allocatable :: omega(:,:), omega_next(:,:)
    real(8), allocatable :: u(:,:), v(:,:), psi_r(:,:)
    real(8), allocatable :: kx(:,:), ky(:,:)
    complex(8), allocatable :: oh(:,:), ph(:,:)
    real(8), pointer :: init_ptr(:) => null()
    ! diagnostics
    real(8) :: ke_sum, ens_sum, max_w, div_sum, n_inv
    complex(8) :: I_UNIT = (0.0_8, 1.0_8)
    complex(8), allocatable :: uh(:,:), vh(:,:), div_s(:,:)
    real(8) :: div_r(0:c_nx-1, 0:c_ny-1)

    nx = c_nx; ny = c_ny; steps = c_steps; mode = c_mode
    lx = c_lx; ly = c_ly; dt = c_dt
    nu    = c_u0 / c_re
    delta = 0.05_8 * ly
    dx    = lx / real(nx, 8)
    dy    = ly / real(ny, 8)

    allocate(omega(0:nx-1, 0:ny-1), omega_next(0:nx-1, 0:ny-1))
    allocate(kx(0:nx-1, 0:ny-1), ky(0:nx-1, 0:ny-1))
    allocate(u(0:nx-1, 0:ny-1), v(0:nx-1, 0:ny-1), psi_r(0:nx-1, 0:ny-1))
    allocate(oh(0:nx-1, 0:ny-1), ph(0:nx-1, 0:ny-1))
    allocate(uh(0:nx-1, 0:ny-1), vh(0:nx-1, 0:ny-1), div_s(0:nx-1, 0:ny-1))

    call make_wavenumbers(nx, ny, dx, dy, kx, ky)

    ! Initial vorticity: from C pointer (row-major i*ny+j) or analytic IC
    if (c_associated(c_init_omega)) then
      call c_f_pointer(c_init_omega, init_ptr, [nx*ny])
      do j = 0, ny-1
        do i = 0, nx-1
          omega(i,j) = init_ptr(i*ny + j)
        end do
      end do
    else
      call initial_conditions(nx, ny, lx, ly, c_u0, delta, c_amp, mode, omega)
    end if

    ! Time integration
    t = 0.0_8
    do s = 1, steps
      call rk4_step(omega, nu, kx, ky, nx, ny, dt, omega_next)
      omega = omega_next
      t = t + dt
    end do

    ! Final field recovery
    oh = cmplx(omega, 0.0_8, kind=8)
    call fft2d(oh, nx, ny, .false.)
    call solve_poisson(oh, kx, ky, nx, ny, ph)
    call fft2d(ph, nx, ny, .true.)
    psi_r = real(ph, kind=8)
    ! recompute ph for velocity (it was overwritten by ifft)
    oh = cmplx(omega, 0.0_8, kind=8)
    call fft2d(oh, nx, ny, .false.)
    call solve_poisson(oh, kx, ky, nx, ny, ph)
    call velocity_from_psi(ph, kx, ky, nx, ny, u, v)

    ! Diagnostics
    n_inv = 1.0_8 / real(nx*ny, 8)
    ke_sum  = 0.0_8; ens_sum = 0.0_8; max_w = 0.0_8
    do j = 0, ny-1
      do i = 0, nx-1
        ke_sum  = ke_sum  + 0.5_8*(u(i,j)**2 + v(i,j)**2)
        ens_sum = ens_sum + 0.5_8*omega(i,j)**2
        if (abs(omega(i,j)) > max_w) max_w = abs(omega(i,j))
      end do
    end do
    c_ke        = ke_sum  * n_inv
    c_enstrophy = ens_sum * n_inv
    c_max_vort  = max_w

    ! Divergence rms
    uh = cmplx(u, 0.0_8, kind=8); call fft2d(uh, nx, ny, .false.)
    vh = cmplx(v, 0.0_8, kind=8); call fft2d(vh, nx, ny, .false.)
    do j = 0, ny-1
      do i = 0, nx-1
        div_s(i,j) = I_UNIT*kx(i,j)*uh(i,j) + I_UNIT*ky(i,j)*vh(i,j)
      end do
    end do
    call fft2d(div_s, nx, ny, .true.)
    div_r = real(div_s, kind=8)
    div_sum = 0.0_8
    do j = 0, ny-1
      do i = 0, nx-1
        div_sum = div_sum + div_r(i,j)**2
      end do
    end do
    c_div_rms = sqrt(div_sum * n_inv)

    ! Copy fields to flat C arrays (row-major: index = i*ny + j)
    do j = 0, ny-1
      do i = 0, nx-1
        c_u(i*ny+j)     = u(i,j)
        c_v(i*ny+j)     = v(i,j)
        c_omega(i*ny+j) = omega(i,j)
        c_psi(i*ny+j)   = psi_r(i,j)
      end do
    end do

    deallocate(omega, omega_next, kx, ky, u, v, psi_r, oh, ph, uh, vh, div_s)
  end subroutine kh_simulate_c

end module kh_physics
