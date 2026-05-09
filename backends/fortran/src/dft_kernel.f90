!> @file   dft_kernel.f90
!> @brief  Canonical DFT reference implementation for lege-artis/fourier
!> @author Petr Yamyang
!> @date   2026-05-09 (v0.1.0)
!>
!> Faithful translation of `shared/canonical-equations/dft.md` Eq. DFT-1:
!>
!>     X[k] = SUM_{n=0..N-1} x[n] * exp(-2*pi*i*k*n/N),  k = 0..N-1
!>
!> Convention: asymmetric forward (no 1/N in forward; 1/N in inverse).
!> Matches OppenheimSchafer3rd section 8.2 and numpy.fft.fft.
!>
!> Implementation discipline (per WORKING-SPEC-v0.3-EN.md section 4.1):
!>   - Code is line-by-line translation of the canonical equation.
!>   - No external library used; only intrinsic exp / cos / sin / cmplx.
!>   - Precision: IEEE 754 binary64 (real(real64) / complex(real64)).
!>   - Compiled with -O0 -fcheck=all -Wall for v0.1.0 reference clarity.
!>   - Source kept ASCII-only: gfortran with -std=f2018 -pedantic byte-counts
!>     against the 132-column line limit, and multi-byte UTF-8 in source
!>     (box-drawing, em-dash, etc.) trips line-truncation errors.
!>
!> Equation -> code mapping (per dft.md section 2):
!>
!>   Math (Eq. DFT-1)              | Code
!>   ------------------------------|------------------------------
!>   Outer sum over k              | do k = 0, nlen - 1
!>   X[k] = 0 initial              | X(k) = (0.0_dp, 0.0_dp)
!>   Inner sum over n              | do n = 0, nlen - 1
!>   Argument -2*pi*k*n/N          | omega = -TWO_PI * real(k * n, dp) / real(nlen, dp)
!>   exp(i*omega) = cos + i*sin    | cmplx(cos(omega), sin(omega), kind=dp)
!>   Multiply x[n] by kernel       | x(n) * cmplx(...)
!>   Accumulate                    | X(k) = X(k) + ...
!>
!> Note: nlen holds the sequence length N from Eq. DFT-1. We do NOT name
!> this variable `N` because Fortran is case-insensitive - `N` would
!> collide with the lowercase loop index `n` (Eq. DFT-1 inner-sum index).
!>
!> @license Apache 2.0 (see LICENSE)

module lege_artis_fourier_dft
    use iso_fortran_env, only: real64
    implicit none
    private
    public :: dft, idft, dp

    ! double precision kind (IEEE 754 binary64)
    integer, parameter :: dp = real64

    ! mathematical constants in dp
    real(dp), parameter :: PI = 4.0_dp * atan(1.0_dp)
    real(dp), parameter :: TWO_PI = 2.0_dp * PI

contains

    !> Forward DFT - direct evaluation of `dft.md` Eq. DFT-1.
    !> @param[in]  x  Input sequence x[0..N-1] of complex(dp)
    !> @return     X  Output sequence X[0..N-1] of complex(dp)
    !> @complexity O(N^2) - direct double-loop evaluation. The FFT (v0.2.0+)
    !>             reduces this to O(N log N) for N = 2^m.
    pure function dft(x) result(X_out)
        complex(dp), intent(in)  :: x(:)
        complex(dp), allocatable :: X_out(:)
        integer  :: nlen, k, n   ! nlen = N (Eq. DFT-1); k, n match equation indices
        real(dp) :: omega

        nlen = size(x)
        allocate(X_out(0:nlen-1))

        ! Outer sum over k (one DFT output per iteration)
        do k = 0, nlen - 1
            X_out(k) = (0.0_dp, 0.0_dp)
            ! Inner sum over n (the canonical Eq. DFT-1 sum)
            do n = 0, nlen - 1
                ! Argument of the kernel: -2*pi*k*n/N (Eq. DFT-1 exponent)
                omega = -TWO_PI * real(k * n, dp) / real(nlen, dp)
                ! Accumulate: x[n] * exp(i*omega) = x[n] * (cos(omega) + i*sin(omega))
                X_out(k) = X_out(k) + x(n + 1) * cmplx(cos(omega), sin(omega), kind=dp)
            end do
        end do
    end function dft

    !> Inverse DFT - `dft.md` Eq. DFT-2 (asymmetric convention, factor 1/N in inverse).
    !> @param[in]  X  Frequency-domain sequence X[0..N-1] of complex(dp)
    !> @return     x  Time-domain sequence x[0..N-1] of complex(dp)
    !> @complexity O(N^2)
    pure function idft(X_in) result(x_out)
        complex(dp), intent(in)  :: X_in(:)
        complex(dp), allocatable :: x_out(:)
        integer  :: nlen, k, n   ! nlen = N (Eq. DFT-2); k, n match equation indices
        real(dp) :: omega

        nlen = size(X_in)
        allocate(x_out(0:nlen-1))

        do n = 0, nlen - 1
            x_out(n) = (0.0_dp, 0.0_dp)
            do k = 0, nlen - 1
                ! Inverse kernel: +2*pi*k*n/N (sign flipped vs forward)
                omega = +TWO_PI * real(k * n, dp) / real(nlen, dp)
                x_out(n) = x_out(n) + X_in(k + 1) * cmplx(cos(omega), sin(omega), kind=dp)
            end do
            ! Asymmetric inverse normalisation: factor 1/N
            x_out(n) = x_out(n) / real(nlen, dp)
        end do
    end function idft

end module lege_artis_fourier_dft
