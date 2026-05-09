!> @file   test_dft_property.f90
!> @brief  Property tests for the DFT kernel - algebraic invariants P1-P4, P7, P8
!> @date   2026-05-09 (v0.1.0)
!>
!> Source kept ASCII-only: gfortran with -std=f2018 -pedantic byte-counts
!> against the 132-column line limit (KB-039).
!>
!> Equation-to-code mapping (per shared/property-tests/dft.md ss3):
!>
!>   P1 Linearity   | DFT(a*x + b*y) == a*DFT(x) + b*DFT(y)
!>   P2 Plancherel  | sum|x|^2 == (1/N)*sum|X|^2
!>   P3 DC bin      | X[0] == sum(x)
!>   P4 Hermitian   | X[N-k] == conj(X[k]) for real input, k=1..N-1
!>   P7 Time-shift  | DFT(x_shifted)[k] == X[k]*exp(-2*pi*i*k*m/N)
!>   P8 Convolution | DFT(circ_conv(x,h)) == DFT(x)*DFT(h) (elementwise)
!>
!> Inputs: locked per SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md ss2.1.
!> Variable naming: nlen = sequence length N (NOT 'N' -- avoids case collision
!>   with loop index 'n' under gfortran -fimplicit-none, per KB-037).
!> Tolerance gate: 1.0e-13 fixed (handoff ss1.5). P2 and P8 use scaled gates.
!>
!> @license Apache 2.0

program test_dft_property
    use lege_artis_fourier_dft, only: dft, dp
    implicit none

    integer :: total = 0
    integer :: failed = 0

    write(*, '(A)') '========================================================='
    write(*, '(A)') ' lege-artis/fourier - DFT property tests (v0.1.0 ref)'
    write(*, '(A)') '========================================================='

    call test_p1_linearity()
    call test_p2_plancherel()
    call test_p3_dc_bin()
    call test_p4_hermitian()
    call test_p7_time_shift()
    call test_p8_convolution()

    write(*, '(A)') '========================================================='
    write(*, '(A, I0, A, I0, A)') ' Result: ', (total - failed), '/', total, ' passed'
    if (failed > 0) then
        write(*, '(A)') ' FAILED.'
        stop 1
    else
        write(*, '(A)') ' All tests PASSED.'
    end if

contains

    ! =========================================================================
    ! P1 Linearity: DFT(alpha*x + beta*y) == alpha*DFT(x) + beta*DFT(y)
    ! Spec: shared/property-tests/dft.md ss3 P1
    ! Inputs (locked, N=8, 1-indexed):
    !   x[n] = n + 2n*i,  y[n] = (3n-1) + (-n)*i,  n=1..8
    !   alpha = (2.5, -0.3),  beta = (-1.0, 1.2)
    ! =========================================================================
    subroutine test_p1_linearity()
        integer, parameter :: nlen = 8
        complex(dp) :: x(nlen), y(nlen), z(nlen)
        complex(dp) :: X_out(nlen), Y_out(nlen), Z_out(nlen), rhs(nlen)
        complex(dp), parameter :: alpha = cmplx(2.5_dp, -0.3_dp, kind=dp)
        complex(dp), parameter :: beta  = cmplx(-1.0_dp,  1.2_dp, kind=dp)
        real(dp), parameter :: tol = 1.0e-13_dp
        integer :: n

        do n = 1, nlen
            x(n) = cmplx(real(n, dp), 2.0_dp * real(n, dp), kind=dp)
            y(n) = cmplx(3.0_dp * real(n, dp) - 1.0_dp, -real(n, dp), kind=dp)
        end do

        ! LHS: DFT(alpha*x + beta*y)
        do n = 1, nlen
            z(n) = alpha * x(n) + beta * y(n)
        end do
        Z_out = dft(z)

        ! RHS: alpha*DFT(x) + beta*DFT(y)
        X_out = dft(x)
        Y_out = dft(y)
        do n = 1, nlen
            rhs(n) = alpha * X_out(n) + beta * Y_out(n)
        end do

        call assert_complex_array_close('test_p1_linearity (N=8)', Z_out, rhs, tol)
    end subroutine

    ! =========================================================================
    ! P2 Plancherel: sum|x|^2 == (1/N)*sum|X|^2
    ! Spec: shared/property-tests/dft.md ss3 P2
    ! Input (locked, N=16, 1-indexed): x[n] = 0.7n + (0.5n-2)*i,  n=1..16
    ! Gate: scaled C*N*eps*max(E_time,E_freq) with C=2 (spec ss3 P2)
    ! =========================================================================
    subroutine test_p2_plancherel()
        integer, parameter :: nlen = 16
        complex(dp) :: x(nlen), X_out(nlen)
        real(dp) :: e_time, e_freq, tol_scaled
        integer :: n

        do n = 1, nlen
            x(n) = cmplx(0.7_dp * real(n, dp), 0.5_dp * real(n, dp) - 2.0_dp, kind=dp)
        end do
        X_out = dft(x)

        ! E_time = sum|x[n]|^2,  E_freq = (1/N)*sum|X[k]|^2
        e_time = 0.0_dp
        e_freq = 0.0_dp
        do n = 1, nlen
            e_time = e_time + real(x(n) * conjg(x(n)), dp)
            e_freq = e_freq + real(X_out(n) * conjg(X_out(n)), dp)
        end do
        e_freq = e_freq / real(nlen, dp)

        ! Scaled gate: C*N*eps*max(E_time,E_freq) with C=2
        tol_scaled = 2.0_dp * real(nlen, dp) * epsilon(1.0_dp) * max(e_time, e_freq)

        call assert_real_close('test_p2_plancherel (N=16)', e_time, e_freq, tol_scaled)
    end subroutine

    ! =========================================================================
    ! P3 DC component: X[0] == sum(x)
    ! Spec: shared/property-tests/dft.md ss3 P3
    ! Input (locked, N=8, 1-indexed): x[n] = n + 0.3n*i,  n=1..8
    ! DC bin: X_out(1) in 1-indexed Fortran = X[0] in 0-indexed math
    ! =========================================================================
    subroutine test_p3_dc_bin()
        integer, parameter :: nlen = 8
        complex(dp) :: x(nlen), X_out(nlen), dc_sum
        real(dp) :: tol
        integer :: n

        do n = 1, nlen
            x(n) = cmplx(real(n, dp), 0.3_dp * real(n, dp), kind=dp)
        end do
        X_out = dft(x)

        ! Direct sum: expected X[0] = sum_{n=0..N-1} x[n]
        dc_sum = (0.0_dp, 0.0_dp)
        do n = 1, nlen
            dc_sum = dc_sum + x(n)
        end do

        ! Gate: C*N*eps*max(|S|,1) with C=1 (spec ss3 P3); floor at 1e-13
        tol = max(real(nlen, dp) * epsilon(1.0_dp) * max(abs(dc_sum), 1.0_dp), 1.0e-13_dp)

        ! X_out(1) = X[0] (DC bin, 1-indexed Fortran = 0-indexed math)
        call assert_complex_close('test_p3_dc_bin (N=8)', X_out(1), dc_sum, tol)
    end subroutine

    ! =========================================================================
    ! P4 Hermitian symmetry for real input: X[N-k] == conj(X[k]), k=1..N-1
    ! Spec: shared/property-tests/dft.md ss3 P4
    ! Input (locked, N=8, 1-indexed): x[n] = 0.5n - 1.5 (real),  n=1..8
    ! Mirror mapping (0-indexed math -> 1-indexed Fortran):
    !   X[k] at X_out(k+1); X[N-k] at X_out(nlen-k+1)
    !   mirror_expected(k+1) = conj(X_out(nlen-k+1))  for k=1..N-1
    ! =========================================================================
    subroutine test_p4_hermitian()
        integer, parameter :: nlen = 8
        complex(dp) :: x(nlen), X_out(nlen), mirror_expected(nlen)
        real(dp), parameter :: tol = 1.0e-13_dp
        integer :: kk

        do kk = 1, nlen
            x(kk) = cmplx(0.5_dp * real(kk, dp) - 1.5_dp, 0.0_dp, kind=dp)
        end do
        X_out = dft(x)

        ! Build Hermitian mirror: mirror_expected(k+1) = conj(X_out(N-k+1))
        mirror_expected(1) = X_out(1)   ! DC not checked by P4; placeholder keeps shape
        do kk = 1, nlen - 1
            mirror_expected(kk + 1) = conjg(X_out(nlen - kk + 1))
        end do

        ! Check k=1..N-1 only (Fortran indices 2..nlen)
        call assert_complex_array_close( &
            'test_p4_hermitian (N=8, k=1..7)', &
            X_out(2:nlen), mirror_expected(2:nlen), tol)
    end subroutine

    ! =========================================================================
    ! P7 Time-shift: DFT(x_shifted)[k] == X[k] * exp(-2*pi*i*k*m/N)
    ! Spec: shared/property-tests/dft.md ss3 P7
    ! Input (locked, N=8, 1-indexed): x[n]=0.4n+(0.7n-1)*i, n=1..8; shift m=3
    ! Circular shift (0-indexed math): y[n] = x[(n-m+N) mod N]
    !   1-indexed Fortran: y(n) = x(mod(n-1-m+nlen, nlen)+1)
    ! =========================================================================
    subroutine test_p7_time_shift()
        integer, parameter :: nlen = 8
        integer, parameter :: m_shift = 3
        complex(dp) :: x(nlen), y(nlen)
        complex(dp) :: X_out(nlen), Y_out(nlen), Y_expected(nlen)
        real(dp), parameter :: pi = 4.0_dp * atan(1.0_dp)
        real(dp), parameter :: two_pi = 2.0_dp * pi
        real(dp), parameter :: tol = 1.0e-13_dp
        real(dp) :: omega_k
        integer :: n, k

        do n = 1, nlen
            x(n) = cmplx(0.4_dp * real(n, dp), 0.7_dp * real(n, dp) - 1.0_dp, kind=dp)
        end do

        ! Circular shift: y[n] = x[(n-m+N) mod N] (0-indexed math)
        ! 1-indexed Fortran: y(n) = x(mod(n-1-m_shift+nlen, nlen)+1)
        do n = 1, nlen
            y(n) = x(mod(n - 1 - m_shift + nlen, nlen) + 1)
        end do

        X_out = dft(x)
        Y_out = dft(y)

        ! Expected: Y[k] = X[k] * exp(-2*pi*i*k*m/N)
        ! 0-indexed k maps to 1-indexed Fortran as k+1
        do k = 0, nlen - 1
            omega_k = -two_pi * real(k * m_shift, dp) / real(nlen, dp)
            Y_expected(k + 1) = X_out(k + 1) * cmplx(cos(omega_k), sin(omega_k), kind=dp)
        end do

        call assert_complex_array_close('test_p7_time_shift (N=8,m=3)', Y_out, Y_expected, tol)
    end subroutine

    ! =========================================================================
    ! P8 Convolution theorem: DFT(circ_conv(x,h)) == DFT(x) * DFT(h)
    ! Spec: shared/property-tests/dft.md ss3 P8
    ! Inputs (locked, N=8, 1-indexed):
    !   x = [1,2,3,4,5,6,7,8] (real)
    !   h = [0.5,1.0,1.5,2.0,1.5,1.0,0.5,0.0] (real)
    ! circ_conv (0-indexed math): z[n] = sum_{mm=0..N-1} x[mm]*h[(n-mm+N) mod N]
    ! Gate: scaled C*N*eps*||x||_inf*||h||_inf with C=4 (spec ss3 P8)
    ! =========================================================================
    subroutine test_p8_convolution()
        integer, parameter :: nlen = 8
        complex(dp) :: x(nlen), h(nlen), z(nlen)
        complex(dp) :: X_out(nlen), H_out(nlen), Z_out(nlen), rhs(nlen)
        real(dp) :: x_norm, h_norm, tol_scaled
        integer :: n, mm

        do n = 1, nlen
            x(n) = cmplx(real(n, dp), 0.0_dp, kind=dp)
        end do
        h(1) = cmplx(0.5_dp, 0.0_dp, kind=dp)
        h(2) = cmplx(1.0_dp, 0.0_dp, kind=dp)
        h(3) = cmplx(1.5_dp, 0.0_dp, kind=dp)
        h(4) = cmplx(2.0_dp, 0.0_dp, kind=dp)
        h(5) = cmplx(1.5_dp, 0.0_dp, kind=dp)
        h(6) = cmplx(1.0_dp, 0.0_dp, kind=dp)
        h(7) = cmplx(0.5_dp, 0.0_dp, kind=dp)
        h(8) = cmplx(0.0_dp, 0.0_dp, kind=dp)

        ! Circular convolution (direct O(N^2)):
        ! z(n+1) = sum_{mm=0..N-1} x(mm+1) * h(mod(n-mm+nlen,nlen)+1)
        do n = 0, nlen - 1
            z(n + 1) = (0.0_dp, 0.0_dp)
            do mm = 0, nlen - 1
                z(n + 1) = z(n + 1) + x(mm + 1) * h(mod(n - mm + nlen, nlen) + 1)
            end do
        end do

        ! LHS: DFT(z)
        Z_out = dft(z)

        ! RHS: DFT(x) * DFT(h)  (elementwise)
        X_out = dft(x)
        H_out = dft(h)
        do n = 1, nlen
            rhs(n) = X_out(n) * H_out(n)
        end do

        ! Scaled gate: C*N*eps*||x||_inf*||h||_inf with C=4
        x_norm = 0.0_dp
        h_norm = 0.0_dp
        do n = 1, nlen
            if (abs(x(n)) > x_norm) x_norm = abs(x(n))
            if (abs(h(n)) > h_norm) h_norm = abs(h(n))
        end do
        tol_scaled = 4.0_dp * real(nlen, dp) * epsilon(1.0_dp) * x_norm * h_norm
        tol_scaled = max(tol_scaled, 1.0e-13_dp)   ! floor per handoff ss1.5

        call assert_complex_array_close('test_p8_convolution (N=8)', Z_out, rhs, tol_scaled)
    end subroutine

    ! =========================================================================
    ! Assertion helpers
    ! total and failed accessed via host association from parent program.
    ! =========================================================================

    !> Assert two complex arrays are element-wise close within tolerance.
    !> Increments total; increments failed on violation.
    subroutine assert_complex_array_close(test_name, actual, expected, tol)
        character(len=*), intent(in) :: test_name
        complex(dp),      intent(in) :: actual(:), expected(:)
        real(dp),         intent(in) :: tol
        real(dp) :: max_err
        integer  :: i, idx

        total = total + 1

        if (size(actual) /= size(expected)) then
            failed = failed + 1
            write(*, '(A, A, A)') ' [FAIL] ', test_name, ' - size mismatch'
            return
        end if

        max_err = 0.0_dp
        idx = 1
        do i = 1, size(actual)
            if (abs(actual(i) - expected(i)) > max_err) then
                max_err = abs(actual(i) - expected(i))
                idx = i
            end if
        end do

        if (max_err > tol) then
            failed = failed + 1
            write(*, '(A, A, A, ES10.3, A, ES10.3, A, I0)') &
                ' [FAIL] ', test_name, &
                ' - max-err = ', max_err, ' > tol = ', tol, ' at idx ', idx - 1
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         actual[idx]   = ', real(actual(idx)), ' + ', aimag(actual(idx)), 'i'
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         expected[idx] = ', real(expected(idx)), ' + ', aimag(expected(idx)), 'i'
        else
            write(*, '(A, A, A, ES10.3, A, ES10.3, A)') &
                ' [PASS] ', test_name, &
                ' - max-err = ', max_err, '  (gate ', tol, ')'
        end if
    end subroutine

    !> Assert a single complex value is within tolerance.
    subroutine assert_complex_close(test_name, actual, expected, tol)
        character(len=*), intent(in) :: test_name
        complex(dp),      intent(in) :: actual, expected
        real(dp),         intent(in) :: tol
        real(dp) :: err

        total = total + 1
        err = abs(actual - expected)
        if (err > tol) then
            failed = failed + 1
            write(*, '(A, A, A, ES10.3, A, ES10.3)') &
                ' [FAIL] ', test_name, ' - err = ', err, ' > tol = ', tol
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         actual   = ', real(actual), ' + ', aimag(actual), 'i'
            write(*, '(A, F12.8, A, F12.8, A)') &
                '         expected = ', real(expected), ' + ', aimag(expected), 'i'
        else
            write(*, '(A, A, A, ES10.3, A, ES10.3, A)') &
                ' [PASS] ', test_name, ' - err = ', err, '  (gate ', tol, ')'
        end if
    end subroutine

    !> Assert two real scalars are within tolerance.
    subroutine assert_real_close(test_name, actual, expected, tol)
        character(len=*), intent(in) :: test_name
        real(dp),         intent(in) :: actual, expected, tol
        real(dp) :: err

        total = total + 1
        err = abs(actual - expected)
        if (err > tol) then
            failed = failed + 1
            write(*, '(A, A, A, ES10.3, A, ES10.3)') &
                ' [FAIL] ', test_name, ' - err = ', err, ' > tol = ', tol
            write(*, '(A, ES14.7, A, ES14.7)') &
                '         actual = ', actual, '  expected = ', expected
        else
            write(*, '(A, A, A, ES10.3, A, ES10.3, A)') &
                ' [PASS] ', test_name, ' - err = ', err, '  (gate ', tol, ')'
        end if
    end subroutine

end program test_dft_property
