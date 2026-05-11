!> @file   test_dft_unit.f90
!> @brief  Unit tests for the DFT kernel - basic correctness on small inputs
!> @date   2026-05-09 (v0.1.0)
!>
!> Source kept ASCII-only: gfortran with -std=f2018 -pedantic byte-counts
!> against the 132-column line limit, and multi-byte UTF-8 characters
!> (box-drawing, em-dash, etc.) push string-literal lines over the limit
!> and trip line-truncation + unterminated-character-constant errors.
!>
!> Tests included:
!>   - test_dft_n4_pure_cosine - the section-1 worked example from
!>     `docs/engineer/en/01-what-dft-actually-computes.md`
!>   - test_dft_n4_dc_input    - DC input (constant) -> DC output
!>   - test_dft_n4_impulse     - impulse -> flat magnitude
!>   - test_dft_n8_pure_cosine - same shape, larger N
!>   - test_dft_idft_roundtrip - inverse recovers input
!>
!> Property-test suite (P1-P8 per shared/property-tests/dft.md) lives in
!> separate files: test_dft_property.f90 (v0.1.0) and test_dft_p5_fft.f90
!> (v0.2.0+ when FFT lands).
!>
!> Compile + run (after Makefile build):
!>   ./build/test_dft_unit
!>
!> @license Apache 2.0

program test_dft_unit
    use lege_artis_fourier_dft, only: dft, idft, dp
    implicit none

    integer :: total = 0
    integer :: failed = 0

    write(*, '(A)') '========================================================='
    write(*, '(A)') ' lege-artis/fourier - DFT unit tests (v0.1.0 reference)'
    write(*, '(A)') '========================================================='

    call test_dft_n4_pure_cosine()
    call test_dft_n4_dc_input()
    call test_dft_n4_impulse_at_centre()
    call test_dft_n8_pure_cosine()
    call test_dft_idft_roundtrip_n8()

    write(*, '(A)') '========================================================='
    write(*, '(A, I0, A, I0, A)') ' Result: ', (total - failed), '/', total, ' passed'
    if (failed > 0) then
        write(*, '(A)') ' FAILED.'
        stop 1
    else
        write(*, '(A)') ' All tests PASSED.'
    end if

contains

    !> Test: DFT of [1, 0, -1, 0] (pure cosine at k=1, N=4)
    !> Expected: X = [0, 2, 0, 2]  (per docs/engineer/en/01-what-dft-actually-computes.md section 1)
    subroutine test_dft_n4_pure_cosine()
        complex(dp) :: x(4), X_out(4), expected(4)
        real(dp), parameter :: tol = 1.0e-13_dp

        x = [(1.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (-1.0_dp, 0.0_dp), (0.0_dp, 0.0_dp)]
        expected = [(0.0_dp, 0.0_dp), (2.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (2.0_dp, 0.0_dp)]

        X_out = dft(x)
        call assert_complex_array_close('test_dft_n4_pure_cosine', X_out, expected, tol)
    end subroutine

    !> Test: DC input [1, 1, 1, 1] -> DC output [4, 0, 0, 0]
    subroutine test_dft_n4_dc_input()
        complex(dp) :: x(4), X_out(4), expected(4)
        real(dp), parameter :: tol = 1.0e-13_dp

        x = [(1.0_dp, 0.0_dp), (1.0_dp, 0.0_dp), (1.0_dp, 0.0_dp), (1.0_dp, 0.0_dp)]
        expected = [(4.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (0.0_dp, 0.0_dp)]

        X_out = dft(x)
        call assert_complex_array_close('test_dft_n4_dc_input', X_out, expected, tol)
    end subroutine

    !> Test: impulse at centre [0, 0, 1, 0] -> DFT has flat magnitude 1
    !> with phases [0, pi, 0, pi] (per shared/physics-testbeds/dft.md PT-DFT-02)
    !> Specifically: X[k] = (-1)^k for impulse at n=2, N=4.
    subroutine test_dft_n4_impulse_at_centre()
        complex(dp) :: x(4), X_out(4), expected(4)
        real(dp), parameter :: tol = 1.0e-13_dp

        x = [(0.0_dp, 0.0_dp), (0.0_dp, 0.0_dp), (1.0_dp, 0.0_dp), (0.0_dp, 0.0_dp)]
        ! X[k] = exp(-2*pi*i*k*2/4) = exp(-pi*i*k) = (-1)^k
        expected = [(1.0_dp, 0.0_dp), (-1.0_dp, 0.0_dp), (1.0_dp, 0.0_dp), (-1.0_dp, 0.0_dp)]

        X_out = dft(x)
        call assert_complex_array_close('test_dft_n4_impulse_at_centre', X_out, expected, tol)
    end subroutine

    !> Test: N=8 cosine at k=1: x[n] = cos(2*pi*1*n/8)
    !> Expected: X[1] = X[7] = 4 = N/2; all others = 0.
    subroutine test_dft_n8_pure_cosine()
        complex(dp) :: x(8), X_out(8), expected(8)
        real(dp), parameter :: tol = 1.0e-13_dp
        real(dp), parameter :: pi = 4.0_dp * atan(1.0_dp)
        integer :: n

        do n = 1, 8
            x(n) = cmplx(cos(2.0_dp * pi * real(n - 1, dp) / 8.0_dp), 0.0_dp, kind=dp)
        end do
        expected = (0.0_dp, 0.0_dp)
        expected(2) = (4.0_dp, 0.0_dp)  ! k=1 (1-indexed: position 2)
        expected(8) = (4.0_dp, 0.0_dp)  ! k=7 (Hermitian mirror)

        X_out = dft(x)
        call assert_complex_array_close('test_dft_n8_pure_cosine', X_out, expected, tol)
    end subroutine

    !> Test: idft(dft(x)) == x within precision (Property P6).
    subroutine test_dft_idft_roundtrip_n8()
        complex(dp) :: x(8), X_freq(8), x_back(8)
        real(dp), parameter :: tol = 1.0e-13_dp
        integer :: n

        ! Arbitrary complex input
        do n = 1, 8
            x(n) = cmplx(real(n, dp) * 0.3_dp, real(n, dp) * 0.5_dp - 1.0_dp, kind=dp)
        end do

        X_freq = dft(x)
        x_back = idft(X_freq)

        call assert_complex_array_close('test_dft_idft_roundtrip_n8', x_back, x, tol)
    end subroutine

    !> Helper: assert two complex arrays are close within tolerance.
    subroutine assert_complex_array_close(test_name, actual, expected, tol)
        character(len=*), intent(in)  :: test_name
        complex(dp),      intent(in)  :: actual(:), expected(:)
        real(dp),         intent(in)  :: tol
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

end program test_dft_unit
