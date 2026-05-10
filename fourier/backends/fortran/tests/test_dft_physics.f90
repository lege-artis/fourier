!> @file   test_dft_physics.f90
!> @brief  Physics testbeds for the DFT kernel - PT-DFT-01/02/03A/03B
!> @date   2026-05-10 (v0.1.0)
!>
!> Source kept ASCII-only (KB-039). Variable naming: nlen = N (KB-037).
!>
!> Testbeds (per shared/physics-testbeds/dft.md):
!>   PT-DFT-01 - Fraunhofer single-slit diffraction
!>               N=64, slit a=16, centred at n=24..39 (0-indexed)
!>   PT-DFT-02 - Heat-equation impulse response
!>               N=64, impulse at n=32 (0-indexed)
!>   PT-DFT-03A - SHO integer frequency, N=64, f0=5
!>               x[n] = cos(2*pi*5*n/64); two-bin concentration
!>   PT-DFT-03B - SHO leakage, N=64, f0=5.5
!>               x[n] = cos(2*pi*5.5*n/64); vs golden vector
!>               (shared/golden-vectors/dft_n=64_cosine_leakage.json)
!>
!> PT-DFT-03B oracle format: output[k] = [Re(X[k]), Im(X[k])], k=0..63.
!> Oracle agreement numpy vs scipy: max_abs_diff = 1.986e-15.
!> Embedded as g_re / g_im DATA blocks (64 values each).
!>
!> @license Apache 2.0

program test_dft_physics
    use lege_artis_fourier_dft, only: dft, dp
    implicit none

    integer :: total = 0
    integer :: failed = 0

    write(*, '(A)') '========================================================='
    write(*, '(A)') ' lege-artis/fourier - DFT physics testbeds (v0.1.0 ref)'
    write(*, '(A)') '========================================================='

    call test_pt01_fraunhofer()
    call test_pt02_heat_impulse()
    call test_pt03a_sho_integer()
    call test_pt03b_cosine_leakage()

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
    ! PT-DFT-01 - Fraunhofer single-slit diffraction
    ! Spec: shared/physics-testbeds/dft.md ss2
    ! Setup: N=64, slit width a=16 centred at n=24..39 (0-indexed)
    !        x[n]=1 for n in {24..39}, x[n]=0 elsewhere
    !        1-indexed Fortran: x(25..40) = 1
    ! Expected:
    !   |X[0]|^2 = 256  (central max)
    !   |X[4]|^2 = 0    (first null; a*k/N = 16*4/64 = 1, integer -> exact zero)
    !   first sidelobe power (k=5..7) in [10, 14]
    !   max sidelobe/peak ratio (k>=5) in [0.04, 0.05]
    ! Gate: 1e-12 (analytical values are exact for integer-ratio parameters)
    ! =========================================================================
    subroutine test_pt01_fraunhofer()
        integer, parameter :: nlen = 64
        complex(dp) :: x(nlen), X_out(nlen)
        real(dp) :: pwr0, pwr4, sidelobe_max, ratio_max, pwr_k
        integer :: n, k

        ! Build aperture: positions 25..40 (1-indexed) = n=24..39 (0-indexed)
        x = (0.0_dp, 0.0_dp)
        do n = 25, 40
            x(n) = (1.0_dp, 0.0_dp)
        end do
        X_out = dft(x)

        ! Assertion 1: central max |X[0]|^2 == 256 within 256*1e-12
        ! X_out(1) = X[0] (DC bin; 1-indexed Fortran = 0-indexed math)
        pwr0 = real(X_out(1) * conjg(X_out(1)), dp)
        call assert_real_close( &
            'PT-DFT-01 central max |X[0]|^2=256', &
            pwr0, 256.0_dp, 256.0_dp * 1.0e-12_dp)

        ! Assertion 2: first null |X[4]|^2 < 1e-12
        ! X_out(5) = X[4] (1-indexed Fortran)
        pwr4 = real(X_out(5) * conjg(X_out(5)), dp)
        call assert_real_close( &
            'PT-DFT-01 first null |X[4]|^2=0', &
            pwr4, 0.0_dp, 1.0e-12_dp)

        ! Assertion 3: first sidelobe between k=4..8 (exclusive -> k=5,6,7)
        ! 1-indexed positions 6..8; spec expects peak in [10, 14]
        sidelobe_max = 0.0_dp
        do k = 6, 8
            pwr_k = real(X_out(k) * conjg(X_out(k)), dp)
            if (pwr_k > sidelobe_max) sidelobe_max = pwr_k
        end do
        call assert_real_in_range( &
            'PT-DFT-01 first sidelobe max power (k=5..7)', &
            sidelobe_max, 10.0_dp, 14.0_dp)

        ! Assertion 4: max sidelobe/peak ratio over k>=5 in [0.04, 0.05]
        ! k>=5 (0-indexed) -> 1-indexed positions 6..64
        ratio_max = 0.0_dp
        do k = 6, nlen
            pwr_k = real(X_out(k) * conjg(X_out(k)), dp)
            if (pwr_k / pwr0 > ratio_max) ratio_max = pwr_k / pwr0
        end do
        call assert_real_in_range( &
            'PT-DFT-01 sidelobe/peak ratio max (k>=5)', &
            ratio_max, 0.04_dp, 0.05_dp)
    end subroutine

    ! =========================================================================
    ! PT-DFT-02 - Heat-equation Green's function (impulse response)
    ! Spec: shared/physics-testbeds/dft.md ss3
    ! Setup: N=64, impulse at n=32 (0-indexed) = position 33 (1-indexed)
    ! Expected: X[k] = exp(-pi*i*k) = (-1)^k
    !   |X[k]| = 1 for all k  (flat magnitude)
    !   Im(X[k]) = 0 for all k (real output)
    !   sign: X[k] > 0 for even k, X[k] < 0 for odd k
    ! Gate: 1.0e-13 (consistent with unit and property test gates)
    ! =========================================================================
    subroutine test_pt02_heat_impulse()
        integer, parameter :: nlen = 64
        real(dp), parameter :: tol = 1.0e-13_dp
        complex(dp) :: x(nlen), X_out(nlen)
        integer :: k, mag_fail, im_fail, sign_fail

        ! Impulse at n=32 (0-indexed) = position 33 (1-indexed)
        x = (0.0_dp, 0.0_dp)
        x(33) = (1.0_dp, 0.0_dp)
        X_out = dft(x)

        ! Check 1: |X[k]| = 1 for all k within tol (aggregate)
        mag_fail = 0
        do k = 1, nlen
            if (abs(abs(X_out(k)) - 1.0_dp) > tol) mag_fail = mag_fail + 1
        end do
        total = total + 1
        if (mag_fail > 0) then
            failed = failed + 1
            write(*, '(A, I0, A, ES10.3)') &
                ' [FAIL] PT-DFT-02 |X[k]|=1: ', mag_fail, ' bins failed, gate ', tol
        else
            write(*, '(A, ES10.3, A)') &
                ' [PASS] PT-DFT-02 |X[k]|=1 for all 64 bins  (gate ', tol, ')'
        end if

        ! Check 2: Im(X[k]) = 0 for all k within tol
        im_fail = 0
        do k = 1, nlen
            if (abs(aimag(X_out(k))) > tol) im_fail = im_fail + 1
        end do
        total = total + 1
        if (im_fail > 0) then
            failed = failed + 1
            write(*, '(A, I0, A, ES10.3)') &
                ' [FAIL] PT-DFT-02 Im(X[k])=0: ', im_fail, ' bins failed, gate ', tol
        else
            write(*, '(A, ES10.3, A)') &
                ' [PASS] PT-DFT-02 Im(X[k])=0 for all 64 bins  (gate ', tol, ')'
        end if

        ! Check 3: sign pattern (-1)^k
        ! even k (0-indexed) -> 1-indexed position k+1; Re(X[k]) > 0
        ! odd  k             -> Re(X[k]) < 0
        sign_fail = 0
        do k = 0, nlen - 1
            if (mod(k, 2) == 0) then
                if (real(X_out(k + 1), dp) <= 0.0_dp) sign_fail = sign_fail + 1
            else
                if (real(X_out(k + 1), dp) >= 0.0_dp) sign_fail = sign_fail + 1
            end if
        end do
        total = total + 1
        if (sign_fail > 0) then
            failed = failed + 1
            write(*, '(A, I0, A)') &
                ' [FAIL] PT-DFT-02 sign(-1)^k: ', sign_fail, ' bins with wrong sign'
        else
            write(*, '(A)') &
                ' [PASS] PT-DFT-02 sign pattern (-1)^k correct for all 64 bins'
        end if
    end subroutine

    ! =========================================================================
    ! PT-DFT-03A - SHO integer frequency (no spectral leakage)
    ! Spec: shared/physics-testbeds/dft.md ss4 setup A
    ! Setup: N=64, f0=5 (integer), x[n] = cos(2*pi*5*n/64), n=0..63
    !        1-indexed Fortran: x(n) = cos(2*pi*5*(n-1)/64)
    ! Expected:
    !   X[5]  = 32.0 + 0.0i (0-indexed k=5 -> 1-indexed position 6)
    !   X[59] = 32.0 + 0.0i (0-indexed k=59 -> 1-indexed position 60)
    !   |X[k]| < 1e-12 for all other k
    !   Plancherel: sum|x|^2 == (1/N)*sum|X|^2
    ! =========================================================================
    subroutine test_pt03a_sho_integer()
        integer, parameter :: nlen = 64
        real(dp), parameter :: pi = 4.0_dp * atan(1.0_dp)
        real(dp), parameter :: tol_bin = 1.0e-12_dp
        complex(dp) :: x(nlen), X_out(nlen)
        real(dp) :: e_time, e_freq, tol_plancherel
        integer :: n, k, other_fail

        ! x[n] = cos(2*pi*5*n/64), n=0..63 (0-indexed math, 1-indexed Fortran)
        do n = 1, nlen
            x(n) = cmplx(cos(2.0_dp * pi * 5.0_dp * real(n - 1, dp) / real(nlen, dp)), &
                         0.0_dp, kind=dp)
        end do
        X_out = dft(x)

        ! X[5] = 32 + 0i: 0-indexed k=5 -> 1-indexed position 6
        call assert_real_close( &
            'PT-DFT-03A X[5] real=32', real(X_out(6), dp), 32.0_dp, tol_bin)
        call assert_real_close( &
            'PT-DFT-03A X[5] imag=0', aimag(X_out(6)), 0.0_dp, tol_bin)

        ! X[59] = 32 + 0i: 0-indexed k=59 -> 1-indexed position 60
        call assert_real_close( &
            'PT-DFT-03A X[59] real=32', real(X_out(60), dp), 32.0_dp, tol_bin)
        call assert_real_close( &
            'PT-DFT-03A X[59] imag=0', aimag(X_out(60)), 0.0_dp, tol_bin)

        ! All other bins |X[k]| < 1e-12
        other_fail = 0
        do k = 1, nlen
            if (k == 6 .or. k == 60) cycle
            if (abs(X_out(k)) >= tol_bin) other_fail = other_fail + 1
        end do
        total = total + 1
        if (other_fail > 0) then
            failed = failed + 1
            write(*, '(A, I0, A, ES10.3)') &
                ' [FAIL] PT-DFT-03A other 62 bins < 1e-12: ', &
                other_fail, ' failed, gate ', tol_bin
        else
            write(*, '(A, ES10.3, A)') &
                ' [PASS] PT-DFT-03A all other 62 bins < ', tol_bin, ' (100% energy in k=5,59)'
        end if

        ! Plancherel: sum|x|^2 == (1/N)*sum|X|^2
        ! Gate: C*N*eps*max(E_time, E_freq) with C=2 (same as P2 property test)
        e_time = 0.0_dp
        e_freq = 0.0_dp
        do n = 1, nlen
            e_time = e_time + real(x(n) * conjg(x(n)), dp)
            e_freq = e_freq + real(X_out(n) * conjg(X_out(n)), dp)
        end do
        e_freq = e_freq / real(nlen, dp)
        tol_plancherel = 2.0_dp * real(nlen, dp) * epsilon(1.0_dp) * max(e_time, e_freq)
        call assert_real_close( &
            'PT-DFT-03A Plancherel', e_time, e_freq, tol_plancherel)
    end subroutine

    ! =========================================================================
    ! PT-DFT-03B - Cosine leakage (non-integer frequency)
    ! Spec: shared/physics-testbeds/dft.md ss4 setup B
    ! Setup: N=64, f0=5.5, x[n] = cos(2*pi*5.5*n/64), n=0..63
    ! Oracle: shared/golden-vectors/dft_n=64_cosine_leakage.json
    !   Embedded as g_re(64) / g_im(64) DATA blocks below.
    !   Format: g_re(k+1) = Re(X[k]), g_im(k+1) = Im(X[k]), k=0..63.
    !   Notable: all Re(X[k]) ~ 1.0 (specific to this cosine / N combination).
    !   Large bins: |X[5]| ~ 19.5, |X[6]| ~ 21.2 (leakage near half-integer f0).
    ! Gate: 1.0e-10 absolute on power spectrum |X[k]|^2 per bin.
    !   Rationale: O(N^2) Fortran kernel vs oracle FFT; per-bin O(N^2*eps) ~ 9e-13;
    !   gate 1e-10 is ~100x margin, appropriate for a profile characterisation test.
    ! =========================================================================
    subroutine test_pt03b_cosine_leakage()
        integer, parameter :: nlen = 64
        real(dp), parameter :: pi = 4.0_dp * atan(1.0_dp)
        real(dp), parameter :: gate = 1.0e-10_dp
        complex(dp) :: x(nlen), X_out(nlen)
        real(dp) :: g_re(64), g_im(64)
        real(dp) :: oracle_pwr, actual_pwr, max_pwr_err
        integer :: n, k, pwr_fail

        ! Oracle Re(X[k]), k=0..63; embedded from JSON output array.
        ! g_re(k+1) = Re(X[k]) in 1-indexed Fortran convention.
        data g_re / &
            1.0000000000000087_dp, 1.0000000000000098_dp, 1.0000000000000102_dp, &
            1.0000000000000124_dp, 1.0000000000000184_dp, 1.0000000000000522_dp, &
            0.9999999999999515_dp, 0.9999999999999858_dp, 0.9999999999999913_dp, &
            0.9999999999999947_dp, 0.9999999999999957_dp, 0.9999999999999973_dp, &
            0.9999999999999976_dp, 0.9999999999999983_dp, 0.9999999999999978_dp, &
            0.9999999999999989_dp, 0.9999999999999989_dp, 0.9999999999999983_dp, &
            0.9999999999999993_dp, 0.9999999999999989_dp, 0.9999999999999993_dp, &
            0.9999999999999996_dp, 0.9999999999999999_dp, 0.9999999999999993_dp, &
            0.9999999999999989_dp, 0.9999999999999987_dp, 0.9999999999999997_dp, &
            1.0_dp, 0.9999999999999989_dp, 0.9999999999999992_dp, &
            1.0_dp, 0.9999999999999986_dp, 0.9999999999999989_dp, &
            0.9999999999999996_dp, 0.9999999999999996_dp, 0.9999999999999991_dp, &
            0.9999999999999989_dp, 0.9999999999999984_dp, 0.9999999999999986_dp, &
            0.9999999999999987_dp, 0.9999999999999989_dp, 0.9999999999999987_dp, &
            0.9999999999999992_dp, 0.9999999999999973_dp, 0.9999999999999993_dp, &
            0.9999999999999986_dp, 0.9999999999999991_dp, 0.9999999999999987_dp, &
            0.9999999999999989_dp, 0.9999999999999986_dp, 0.999999999999998_dp, &
            0.9999999999999984_dp, 0.9999999999999976_dp, 0.999999999999996_dp, &
            0.9999999999999963_dp, 0.999999999999994_dp, 0.9999999999999913_dp, &
            0.9999999999999858_dp, 0.9999999999999517_dp, 1.0000000000000515_dp, &
            1.0000000000000184_dp, 1.0000000000000129_dp, 1.0000000000000102_dp, &
            1.0000000000000098_dp /

        ! Oracle Im(X[k]), k=0..63; embedded from JSON output array.
        data g_im / &
            0.0_dp, 0.7130795100483178_dp, 1.5853697436903686_dp, &
            2.925910975873875_dp, 5.785005225004534_dp, 19.485118500994588_dp, &
            -21.157328220021725_dp, -7.488280072923256_dp, -4.694583691856731_dp, &
            -3.4612099562261216_dp, -2.7517675353271347_dp, -2.2828074140041767_dp, &
            -1.9448245682872571_dp, -1.6864050886960076_dp, -1.4801216563971011_dp, &
            -1.309950904260467_dp, -1.165869936412268_dp, -1.041265133879751_dp, &
            -0.9315802086924778_dp, -0.8335620731538382_dp, -0.7448166423388842_dp, &
            -0.6635350581901365_dp, -0.5883183280090254_dp, -0.5180611961972974_dp, &
            -0.4518729478953416_dp, -0.3890219461937474_dp, -0.3288958191432467_dp, &
            -0.27097219031070807_dp, -0.21479663413842331_dp, -0.1599656388770634_dp, &
            -0.10611305306663266_dp, -0.052898934013602295_dp, 0.0_dp, &
            0.05289893401360213_dp, 0.10611305306663277_dp, 0.15996563887706272_dp, &
            0.21479663413842331_dp, 0.27097219031070985_dp, 0.3288958191432467_dp, &
            0.3890219461937465_dp, 0.4518729478953416_dp, 0.5180611961972981_dp, &
            0.5883183280090254_dp, 0.6635350581901367_dp, 0.7448166423388842_dp, &
            0.8335620731538383_dp, 0.9315802086924784_dp, 1.0412651338797512_dp, &
            1.165869936412268_dp, 1.3099509042604667_dp, 1.4801216563971007_dp, &
            1.6864050886960076_dp, 1.9448245682872571_dp, 2.2828074140041767_dp, &
            2.7517675353271347_dp, 3.461209956226122_dp, 4.694583691856731_dp, &
            7.488280072923256_dp, 21.157328220021725_dp, -19.485118500994588_dp, &
            -5.785005225004534_dp, -2.9259109758738746_dp, -1.5853697436903689_dp, &
            -0.713079510048318_dp /

        ! Build input: x[n] = cos(2*pi*5.5*n/64), n=0..63 (0-indexed math)
        ! 1-indexed Fortran: x(n) = cos(2*pi*5.5*(n-1)/64)
        do n = 1, nlen
            x(n) = cmplx( &
                cos(2.0_dp * pi * 5.5_dp * real(n - 1, dp) / real(nlen, dp)), &
                0.0_dp, kind=dp)
        end do
        X_out = dft(x)

        ! Compare power spectrum |X[k]|^2 vs oracle power, gate=1e-10 per bin
        ! g_re(k+1) / g_im(k+1) are oracle Re/Im for 0-indexed k
        max_pwr_err = 0.0_dp
        pwr_fail = 0
        do k = 1, nlen
            oracle_pwr = g_re(k) * g_re(k) + g_im(k) * g_im(k)
            actual_pwr = real(X_out(k) * conjg(X_out(k)), dp)
            if (abs(actual_pwr - oracle_pwr) > gate) pwr_fail = pwr_fail + 1
            if (abs(actual_pwr - oracle_pwr) > max_pwr_err) &
                max_pwr_err = abs(actual_pwr - oracle_pwr)
        end do

        total = total + 1
        if (pwr_fail > 0) then
            failed = failed + 1
            write(*, '(A, I0, A, ES10.3, A, ES10.3)') &
                ' [FAIL] PT-DFT-03B leakage: ', pwr_fail, &
                ' bins failed, max_pwr_err = ', max_pwr_err, ' > gate ', gate
        else
            write(*, '(A, ES10.3, A, ES10.3, A)') &
                ' [PASS] PT-DFT-03B leakage profile 64 bins: max_pwr_err = ', &
                max_pwr_err, '  (gate ', gate, ')'
        end if
    end subroutine

    ! =========================================================================
    ! Assertion helpers -- total / failed via host association from parent program
    ! =========================================================================

    !> Assert two real scalars are close within tolerance.
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

    !> Assert a real value falls within [lo, hi].
    subroutine assert_real_in_range(test_name, val, lo, hi)
        character(len=*), intent(in) :: test_name
        real(dp),         intent(in) :: val, lo, hi

        total = total + 1
        if (val >= lo .and. val <= hi) then
            write(*, '(A, A, A, ES10.3, A, ES10.3, A, ES10.3, A)') &
                ' [PASS] ', test_name, ' - val = ', val, &
                '  in [', lo, ', ', hi, ']'
        else
            failed = failed + 1
            write(*, '(A, A, A, ES10.3, A, ES10.3, A, ES10.3, A)') &
                ' [FAIL] ', test_name, ' - val = ', val, &
                '  NOT in [', lo, ', ', hi, ']'
        end if
    end subroutine

end program test_dft_physics
