import os

import numpy as np
import pytest

import autoarray as aa
from autoarray import exc

test_data_dir = "{}/../test_files/array/".format(
    os.path.dirname(os.path.realpath(__file__))
)

class TestConstructors(object):
    def test__init__input_kernel__all_attributes_correct_including_data_inheritance(
        self
    ):
        kernel = aa.Kernel.from_2d_and_pixel_scale(
            array_2d=np.ones((3, 3)), pixel_scale=1.0, renormalize=False
        )

        assert kernel.in_2d.shape == (3, 3)
        assert (kernel.in_2d == np.ones((3, 3))).all()
        assert kernel.mask.geometry.pixel_scales == (1.0, 1.0)
        assert kernel.mask.origin == (0.0, 0.0)

        kernel = aa.Kernel.from_2d_and_pixel_scale(
            array_2d=np.ones((4, 3)), pixel_scale=1.0, renormalize=False
        )

        assert kernel.in_2d.shape == (4, 3)
        assert (kernel.in_2d == np.ones((4, 3))).all()
        assert kernel.mask.geometry.pixel_scales == (1.0, 1.0)
        assert kernel.mask.origin == (0.0, 0.0)

    def test__from_fits__input_kernel_3x3__all_attributes_correct_including_data_inheritance(
        self
    ):
        kernel = aa.Kernel.from_fits_and_pixel_scale(
            file_path=test_data_dir + "3x3_ones.fits", hdu=0, pixel_scale=1.0
        )

        assert (kernel.in_2d == np.ones((3, 3))).all()

        kernel = aa.Kernel.from_fits_and_pixel_scale(
            file_path=test_data_dir + "4x3_ones.fits", hdu=0, pixel_scale=1.0
        )

        assert (kernel.in_2d == np.ones((4, 3))).all()


class TestRenormalize(object):
    def test__input_is_already_normalized__no_change(self):

        kernel_data = np.ones((3, 3)) / 9.0
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel_data, pixel_scale=1.0, renormalize=True)

        assert kernel.in_2d == pytest.approx(kernel_data, 1e-3)

    def test__input_is_above_normalization_so_is_normalized(self):

        kernel_data =np.ones((3, 3))

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel_data, pixel_scale=1.0, renormalize=True)

        assert kernel.in_2d == pytest.approx(np.ones((3, 3)) / 9.0, 1e-3)

    def test__same_as_above__renomalized_false_does_not_renormalize(self):
        kernel_data = np.ones((3, 3))

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel_data, pixel_scale=1.0, renormalize=False)

        assert kernel.in_2d == pytest.approx(np.ones((3, 3)), 1e-3)


class TestBinnedUp(object):
    def test__kernel_is_even_x_even__rescaled_to_odd_x_odd__no_use_of_dimension_trimming(
        self
    ):
        array_2d = np.ones((6, 6))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.5, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 2.0
        assert (kernel.in_2d == (1.0 / 9.0) * np.ones((3, 3))).all()

        array_2d = np.ones((9, 9))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.333333333333333, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 3.0
        assert (kernel.in_2d == (1.0 / 9.0) * np.ones((3, 3))).all()

        array_2d = np.ones((18, 6))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.5, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 2.0
        assert (kernel.in_2d == (1.0 / 27.0) * np.ones((9, 3))).all()

        array_2d = np.ones((6, 18))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.5, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 2.0
        assert (kernel.in_2d == (1.0 / 27.0) * np.ones((3, 9))).all()

    def test__kernel_is_even_x_even_after_binning_up__resized_to_odd_x_odd_with_shape_plus_one(
        self
    ):
        array_2d = np.array(np.ones((2, 2)))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=2.0, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 0.4
        assert (kernel.in_2d == (1.0 / 25.0) * np.ones((5, 5))).all()

        array_2d = np.ones((40, 40))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.1, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scale == 8.0
        assert (kernel.in_2d == (1.0 / 25.0) * np.ones((5, 5))).all()

        array_2d = np.ones((2, 4))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=2.0, renormalize=True
        )

        assert kernel.mask.geometry.pixel_scales[0] == pytest.approx(0.4, 1.0e-4)
        assert kernel.mask.geometry.pixel_scales[1] == pytest.approx(0.4444444, 1.0e-4)
        assert (kernel.in_2d == (1.0 / 45.0) * np.ones((5, 9))).all()

        array_2d = np.array(np.ones((4, 2)))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=2.0, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scales[0] == pytest.approx(0.4444444, 1.0e-4)
        assert kernel.mask.geometry.pixel_scales[1] == pytest.approx(0.4, 1.0e-4)
        assert (kernel.in_2d == (1.0 / 45.0) * np.ones((9, 5))).all()

    def test__kernel_is_odd_and_even_after_binning_up__resized_to_odd_and_odd_with_shape_plus_one(
        self
    ):
        array_2d = np.array(np.ones((6, 4)))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.5, renormalize=True
        )

        assert kernel.mask.geometry.pixel_scales == pytest.approx((2.0, 1.3333333333), 1.0e-4)
        assert (kernel.in_2d == (1.0 / 9.0) * np.ones((3, 3))).all()

        array_2d = np.ones((9, 12))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.33333333333, renormalize=True
        )

        assert kernel.mask.geometry.pixel_scales == pytest.approx((3.0, 2.4), 1.0e-4)
        assert (kernel.in_2d == (1.0 / 15.0) * np.ones((3, 5))).all()

        array_2d = np.array(np.ones((4, 6)))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.5, renormalize=True
        )

        assert kernel.mask.geometry.pixel_scales == pytest.approx((1.33333333333, 2.0), 1.0e-4)
        assert (kernel.in_2d == (1.0 / 9.0) * np.ones((3, 3))).all()

        array_2d = np.ones((12, 9))
        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=array_2d, pixel_scale=1.0, renormalize=False)
        kernel = kernel.rescaled_with_odd_dimensions_from_rescale_factor(
            rescale_factor=0.33333333333, renormalize=True
        )
        assert kernel.mask.geometry.pixel_scales == pytest.approx((2.4, 3.0), 1.0e-4)
        assert (kernel.in_2d == (1.0 / 15.0) * np.ones((5, 3))).all()


class TestConvolve(object):
    def test__kernel_is_not_odd_x_odd__raises_error(self):
        kernel = np.array([[0.0, 1.0], [1.0, 2.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        with pytest.raises(exc.KernelException):
            kernel.convolved_array_from_array(np.ones((5, 5)))

    def test__image_is_3x3_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
        self
    ):
        
        image = aa.Array.from_array_2d([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (blurred_image == kernel).all()

    def test__image_is_4x4_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
        self
    ):
        image = aa.Array.from_array_2d(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        )

        kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [
                    [0.0, 1.0, 0.0, 0.0],
                    [1.0, 2.0, 1.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0],
                ]
            )
        ).all()

    def test__image_is_4x3_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
        self
    ):
        image = aa.Array.from_array_2d(
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        )

        kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
            )
        ).all()

    def test__image_is_3x4_central_value_of_one__kernel_is_cross__blurred_image_becomes_cross(
        self
    ):
        image = aa.Array.from_array_2d(
            [[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        )

        kernel = np.array([[0.0, 1.0, 0.0], [1.0, 2.0, 1.0], [0.0, 1.0, 0.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [[0.0, 1.0, 0.0, 0.0], [1.0, 2.0, 1.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
            )
        ).all()

    def test__image_is_4x4_has_two_central_values__kernel_is_asymmetric__blurred_image_follows_convolution(
        self
    ):
        image = aa.Array.from_array_2d(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        )

        kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [
                    [1.0, 1.0, 1.0, 0.0],
                    [2.0, 3.0, 2.0, 1.0],
                    [1.0, 5.0, 5.0, 1.0],
                    [0.0, 1.0, 3.0, 3.0],
                ]
            )
        ).all()

    def test__image_is_4x4_values_are_on_edge__kernel_is_asymmetric__blurring_does_not_account_for_edge_effects(
        self
    ):
        image = aa.Array.from_array_2d(
            [
                [0.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        )

        kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [
                    [1.0, 1.0, 0.0, 0.0],
                    [2.0, 1.0, 1.0, 1.0],
                    [3.0, 3.0, 2.0, 2.0],
                    [0.0, 0.0, 1.0, 3.0],
                ]
            )
        ).all()

    def test__image_is_4x4_values_are_on_corner__kernel_is_asymmetric__blurring_does_not_account_for_edge_effects(
        self
    ):
        image = aa.Array.from_array_2d(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        kernel = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 1.0], [1.0, 3.0, 3.0]])

        kernel = aa.Kernel.from_2d_and_pixel_scale(array_2d=kernel, pixel_scale=1.0)

        blurred_image = kernel.convolved_array_from_array(image)

        assert (
            blurred_image.in_2d
            == np.array(
                [
                    [2.0, 1.0, 0.0, 0.0],
                    [3.0, 3.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 1.0],
                    [0.0, 0.0, 2.0, 2.0],
                ]
            )
        ).all()


class TestFromKernelNoBlurring(object):
    def test__correct_kernel(self):
        kernel = aa.Kernel.from_no_blurring_kernel(pixel_scale=1.0)

        assert (
            kernel.in_2d
            == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        ).all()
        assert kernel.mask.geometry.pixel_scale == 1.0

        kernel = aa.Kernel.from_no_blurring_kernel(pixel_scale=2.0)

        assert (
            kernel.in_2d
            == np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        ).all()
        assert kernel.mask.geometry.pixel_scale == 2.0

# class TestFromGaussian(object):
#     def test__identical_to_gaussian_light_profile(self):
#         grid = aa.SubGrid.from_shape_pixel_scale_and_sub_size(
#             shape=(3, 3), pixel_scale=1.0, sub_size=1
#         )
#
#         gaussian = aa.light_profiles.EllipticalGaussian(
#             centre=(0.1, 0.1), axis_ratio=0.9, phi=45.0, intensity=1.0, sigma=1.0
#         )
#         profile_gaussian = gaussian.profile_image_from_grid(grid=grid)
#
#         profile_kernel = aa.Kernel.from_2d_and_pixel_scale(
#             array_2d=profile_gaussian.in_2d, renormalize=True
#         )
#
#         imaging_kernel = aa.Kernel.from_gaussian(
#             shape=(3, 3),
#             pixel_scale=1.0,
#             centre=(0.1, 0.1),
#             axis_ratio=0.9,
#             phi=45.0,
#             sigma=1.0,
#         )
#
#         assert profile_kernel.in_2d == pytest.approx(imaging_kernel.in_2d, 1e-4)
#
# class TestFromAlmaGaussian(object):
#     def test__identical_to_astropy_gaussian_model__circular_no_rotation(self):
#         pixel_scale = 0.1
#
#         x_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=2.0,
#             y_mean=2.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=0.0,
#         )
#
#         shape = (5, 5)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=2.0e-5,
#             theta=0.0,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)
#
#     def test__identical_to_astropy_gaussian_model__circular_no_rotation_different_pixel_scale(
#         self
#     ):
#         pixel_scale = 0.02
#
#         x_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=2.0,
#             y_mean=2.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=0.0,
#         )
#
#         shape = (5, 5)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=2.0e-5,
#             theta=0.0,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)
#
#     def test__identical_to_astropy_gaussian_model__include_ellipticity_from_x_and_y_stddev(
#         self
#     ):
#         pixel_scale = 0.1
#
#         x_stddev = (
#             1.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         theta_deg = 0.0
#         theta = Angle(theta_deg, "deg").radian
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=2.0,
#             y_mean=2.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=theta,
#         )
#
#         shape = (5, 5)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=1.0e-5,
#             theta=theta_deg,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)
#
#     def test__identical_to_astropy_gaussian_model__include_different_ellipticity_from_x_and_y_stddev(
#         self
#     ):
#         pixel_scale = 0.1
#
#         x_stddev = (
#             3.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         theta_deg = 0.0
#         theta = Angle(theta_deg, "deg").radian
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=2.0,
#             y_mean=2.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=theta,
#         )
#
#         shape = (5, 5)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=3.0e-5,
#             theta=theta_deg,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)
#
#     def test__identical_to_astropy_gaussian_model__include_rotation_angle_30(self):
#         pixel_scale = 0.1
#
#         x_stddev = (
#             1.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         theta_deg = 30.0
#         theta = Angle(theta_deg, "deg").radian
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=1.0,
#             y_mean=1.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=theta,
#         )
#
#         shape = (3, 3)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=1.0e-5,
#             theta=theta_deg,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)
#
#     def test__identical_to_astropy_gaussian_model__include_rotation_angle_230(self):
#         pixel_scale = 0.1
#
#         x_stddev = (
#             1.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#         y_stddev = (
#             2.0e-5
#             * (units.deg).to(units.arcsec)
#             / pixel_scale
#             / (2.0 * np.sqrt(2.0 * np.log(2.0)))
#         )
#
#         theta_deg = 230.0
#         theta = Angle(theta_deg, "deg").radian
#
#         gaussian_astropy = functional_models.Gaussian2D(
#             amplitude=1.0,
#             x_mean=1.0,
#             y_mean=1.0,
#             x_stddev=x_stddev,
#             y_stddev=y_stddev,
#             theta=theta,
#         )
#
#         shape = (3, 3)
#         y, x = np.mgrid[0 : shape[1], 0 : shape[0]]
#         kernel_astropy = gaussian_astropy(x, y)
#         kernel_astropy /= np.sum(kernel_astropy)
#
#         kernel = aa.Kernel.from_as_gaussian_via_alma_fits_header_parameters(
#             shape=shape,
#             pixel_scale=pixel_scale,
#             y_stddev=2.0e-5,
#             x_stddev=1.0e-5,
#             theta=theta_deg,
#         )
#
#         assert kernel_astropy == pytest.approx(kernel.in_2d, 1e-4)