import numpy as np
from functools import wraps

from autoconf import conf
from autoarray.structures.grids.one_d import abstract_grid_1d
from autoarray.structures.grids.two_d import grid_2d
from autoarray.structures.grids.two_d import grid_2d_interpolate
from autoarray.structures.grids.two_d import grid_2d_iterate
from autoarray.structures.grids.two_d import grid_2d_irregular
from autoarray.structures.arrays.one_d import array_1d
from autoarray.structures.arrays import values

from autoarray import exc

from typing import Union


def grid_1d_to_structure(func):
    """
    Homogenize the inputs and outputs of functions that take 2D grids of (y,x) coordinates that return the results
    as a NumPy array.

    Parameters
    ----------
    func : (obj, grid, *args, **kwargs) -> Object
        A function which computes a set of values from a 2D grid of (y,x) coordinates.

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(
        obj, grid, *args, **kwargs
    ) -> Union[array_1d.Array1D, values.ValuesIrregular]:
        """
        This decorator homogenizes the input of a "grid_like" 2D structure (`Grid2D`, `Grid2DIterate`,
        `Grid2DInterpolate`, `Grid2DIrregular` or `AbstractGrid1D`) into a function. It allows these classes to be
        interchangeably input into a function, such that the grid is used to evaluate the function at every (y,x)
        coordinates of the grid using specific functionality of the input grid.

        The grid_like objects `Grid2D` and `Grid2DIrregular` are input into the function as a slimmed 2D NumPy array
        of shape [total_coordinates, 2] where the second dimension stores the (y,x) values. If a `Grid2DIterate` is
        input, the function is evaluated using the appropriate iterated_*_from_func* function.

        The outputs of the function are converted from a 1D or 2D NumPy Array2D to an `Array2D`, `Grid2D`,
        `ValuesIrregular` or `Grid2DIrregular` objects, whichever is applicable as follows:

        - If the function returns (y,x) coordinates at every input point, the returned results are a `Grid2D`
        or `Grid2DIrregular` structure, the same structure as the input.

        - If the function returns scalar values at every input point and a `Grid2D` is input, the returned results are
        an `Array2D` structure which uses the same dimensions and mask as the `Grid2D`.

        - If the function returns scalar values at every input point and `Grid2DIrregular` are input, the returned
        results are a `ValuesIrregular` object with structure resembling that of the `Grid2DIrregular`.

        If the input array is not a `Grid2D` structure (e.g. it is a 2D NumPy array) the output is a NumPy array.

        Parameters
        ----------
        obj : object
            An object whose function uses grid_like inputs to compute quantities at every coordinate on the grid.
        grid : Grid2D or Grid2DIrregular
            A grid_like object of (y,x) coordinates on which the function values are evaluated.

        Returns
        -------
            The function values evaluated on the grid with the same structure as the input grid_like object.
        """

        centre = (0.0, 0.0)

        if hasattr(obj, "centre"):
            if obj.centre is not None:
                centre = obj.centre

        angle = 0.0

        if hasattr(obj, "angle"):
            if obj.angle is not None:
                angle = obj.angle + 90.0

        if (
            isinstance(grid, grid_2d.Grid2D)
            or isinstance(grid, grid_2d_iterate.Grid2DIterate)
            or isinstance(grid, grid_2d_interpolate.Grid2DInterpolate)
        ):
            grid_2d_projected = grid.grid_2d_radial_projected_from(
                centre=centre, angle=angle
            )
            result = func(obj, grid_2d_projected, *args, **kwargs)
            return array_1d.Array1D.manual_slim(
                array=result, pixel_scales=grid.pixel_scale
            )

        elif isinstance(grid, grid_2d_irregular.Grid2DIrregular):
            result = func(obj, grid, *args, **kwargs)
            return grid.structure_2d_from_result(result=result)
        elif isinstance(grid, abstract_grid_1d.AbstractGrid1D):
            grid_2d_radial = grid.project_to_radial_grid_2d(angle=angle)
            result = func(obj, grid_2d_radial, *args, **kwargs)
            return array_1d.Array1D.manual_slim(
                array=result, pixel_scales=grid.pixel_scale
            )

        raise exc.GridException(
            "You cannot input a NumPy array to a `quantity_1d_from_grid` method."
        )

    return wrapper


def grid_1d_output_structure(func):
    """
    Homogenize the inputs and outputs of functions that take 2D grids of (y,x) coordinates that return the results
    as a NumPy array.

    Parameters
    ----------
    func : (obj, grid, *args, **kwargs) -> Object
        A function which computes a set of values from a 2D grid of (y,x) coordinates.

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(
        obj, grid, *args, **kwargs
    ) -> Union[array_1d.Array1D, values.ValuesIrregular]:
        """
        This decorator homogenizes the input of a "grid_like" 2D structure (`Grid2D`, `Grid2DIterate`,
        `Grid2DInterpolate`, `Grid2DIrregular` or `AbstractGrid1D`) into a function. It allows these classes to be
        interchangeably input into a function, such that the grid is used to evaluate the function at every (y,x)
        coordinates of the grid using specific functionality of the input grid.

        The grid_like objects `Grid2D` and `Grid2DIrregular` are input into the function as a slimmed 2D NumPy array
        of shape [total_coordinates, 2] where the second dimension stores the (y,x) values. If a `Grid2DIterate` is
        input, the function is evaluated using the appropriate iterated_*_from_func* function.

        The outputs of the function are converted from a 1D or 2D NumPy Array2D to an `Array2D`, `Grid2D`,
        `ValuesIrregular` or `Grid2DIrregular` objects, whichever is applicable as follows:

        - If the function returns (y,x) coordinates at every input point, the returned results are a `Grid2D`
        or `Grid2DIrregular` structure, the same structure as the input.

        - If the function returns scalar values at every input point and a `Grid2D` is input, the returned results are
        an `Array2D` structure which uses the same dimensions and mask as the `Grid2D`.

        - If the function returns scalar values at every input point and `Grid2DIrregular` are input, the returned
        results are a `ValuesIrregular` object with structure resembling that of the `Grid2DIrregular`.

        If the input array is not a `Grid2D` structure (e.g. it is a 2D NumPy array) the output is a NumPy array.

        Parameters
        ----------
        obj : object
            An object whose function uses grid_like inputs to compute quantities at every coordinate on the grid.
        grid : Grid2D or Grid2DIrregular
            A grid_like object of (y,x) coordinates on which the function values are evaluated.

        Returns
        -------
            The function values evaluated on the grid with the same structure as the input grid_like object.
        """

        result = func(obj, grid, *args, **kwargs)

        if (
            isinstance(grid, grid_2d.Grid2D)
            or isinstance(grid, grid_2d_iterate.Grid2DIterate)
            or isinstance(grid, grid_2d_interpolate.Grid2DInterpolate)
        ):
            return array_1d.Array1D.manual_slim(
                array=result, pixel_scales=grid.pixel_scale
            )

        elif isinstance(grid, grid_2d_irregular.Grid2DIrregular):
            return grid.structure_2d_from_result(result=result)
        elif isinstance(grid, abstract_grid_1d.AbstractGrid1D):
            return array_1d.Array1D.manual_slim(
                array=result, pixel_scales=grid.pixel_scale
            )

        raise exc.GridException(
            "You cannot input a NumPy array to a `quantity_1d_from_grid` method."
        )

    return wrapper


def grid_2d_to_structure(func):
    """
    Homogenize the inputs and outputs of functions that take 2D grids of (y,x) coordinates that return the results
    as a NumPy array.

    Parameters
    ----------
    func : (obj, grid, *args, **kwargs) -> Object
        A function which computes a set of values from a 2D grid of (y,x) coordinates.

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(obj, grid, *args, **kwargs):
        """
        This decorator homogenizes the input of a "grid_like" 2D structure (`Grid2D`, `Grid2DIterate`,
        `Grid2DInterpolate`, `Grid2DIrregular` or `AbstractGrid1D`) into a function. It allows these classes to be
        interchangeably input into a function, such that the grid is used to evaluate the function at every (y,x)
        coordinates of the grid using specific functionality of the input grid.

        The grid_like objects `Grid2D` and `Grid2DIrregular` are input into the function as a slimmed 2D NumPy array
        of shape [total_coordinates, 2] where the second dimension stores the (y,x) values. If a `Grid2DIterate` is
        input, the function is evaluated using the appropriate iterated_*_from_func* function.

        The outputs of the function are converted from a 1D or 2D NumPy Array2D to an `Array2D`, `Grid2D`,
        `ValuesIrregular` or `Grid2DIrregular` objects, whichever is applicable as follows:

        - If the function returns (y,x) coordinates at every input point, the returned results are a `Grid2D`
        or `Grid2DIrregular` structure, the same structure as the input.

        - If the function returns scalar values at every input point and a `Grid2D` is input, the returned results are
        an `Array2D` structure which uses the same dimensions and mask as the `Grid2D`.

        - If the function returns scalar values at every input point and `Grid2DIrregular` are input, the returned
        results are a `ValuesIrregular` object with structure resembling that of the `Grid2DIrregular`.

        If the input array is not a `Grid2D` structure (e.g. it is a 2D NumPy array) the output is a NumPy array.

        Parameters
        ----------
        obj : object
            An object whose function uses grid_like inputs to compute quantities at every coordinate on the grid.
        grid : Grid2D or Grid2DIrregular
            A grid_like object of (y,x) coordinates on which the function values are evaluated.

        Returns
        -------
            The function values evaluated on the grid with the same structure as the input grid_like object.
        """

        if isinstance(grid, grid_2d_iterate.Grid2DIterate):
            return grid.iterated_result_from_func(func=func, cls=obj)
        elif isinstance(grid, grid_2d_interpolate.Grid2DInterpolate):
            return grid.result_from_func(func=func, cls=obj)
        elif isinstance(grid, grid_2d_irregular.Grid2DIrregular):
            result = func(obj, grid, *args, **kwargs)
            return grid.structure_2d_from_result(result=result)
        elif isinstance(grid, grid_2d.Grid2D):
            result = func(obj, grid, *args, **kwargs)
            return grid.structure_2d_from_result(result=result)
        elif isinstance(grid, abstract_grid_1d.AbstractGrid1D):
            grid_2d_radial = grid.project_to_radial_grid_2d()
            result = func(obj, grid_2d_radial, *args, **kwargs)
            return grid.structure_2d_from_result(result=result)

        if not isinstance(grid, grid_2d_irregular.Grid2DIrregular) and not isinstance(
            grid, grid_2d.Grid2D
        ):
            return func(obj, grid, *args, **kwargs)

    return wrapper


def grid_2d_to_structure_list(func):
    """
    Homogenize the inputs and outputs of functions that take 2D grids of (y,x) coordinates and return the results as
    a list of NumPy arrays.

    Parameters
    ----------
    func : (obj, grid, *args, **kwargs) -> Object
        A function which computes a set of values from a 2D grid of (y,x) coordinates.

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(obj, grid, *args, **kwargs):
        """
        This decorator serves the same purpose as the `grid_2d_to_structure` decorator, but it deals with functions whose
        output is a list of results as opposed to a single NumPy array. It simply iterates over these lists to perform
        the same conversions as `grid_2d_to_structure`.

        Parameters
        ----------
        obj : object
            An object whose function uses grid_like inputs to compute quantities at every coordinate on the grid.
        grid : Grid2D or Grid2DIrregular
            A grid_like object of (y,x) coordinates on which the function values are evaluated.

        Returns
        -------
            The function values evaluated on the grid with the same structure as the input grid_like object in a list
            of NumPy arrays.
        """

        if isinstance(grid, grid_2d_iterate.Grid2DIterate):
            mask = grid.mask.mask_new_sub_size_from(
                mask=grid.mask, sub_size=max(grid.sub_steps)
            )
            grid_compute = grid_2d.Grid2D.from_mask(mask=mask)
            result_list = func(obj, grid_compute, *args, **kwargs)
            result_list = [
                grid_compute.structure_2d_from_result(result=result)
                for result in result_list
            ]
            result_list = [result.binned for result in result_list]
            return grid.grid.structure_2d_list_from_result_list(result_list=result_list)
        elif isinstance(grid, grid_2d_interpolate.Grid2DInterpolate):
            return func(obj, grid, *args, **kwargs)
        elif isinstance(grid, grid_2d_irregular.Grid2DIrregular):
            result_list = func(obj, grid, *args, **kwargs)
            return grid.structure_2d_list_from_result_list(result_list=result_list)
        elif isinstance(grid, grid_2d.Grid2D):
            result_list = func(obj, grid, *args, **kwargs)
            return grid.structure_2d_list_from_result_list(result_list=result_list)
        elif isinstance(grid, abstract_grid_1d.AbstractGrid1D):
            grid_2d_radial = grid.project_to_radial_grid_2d()
            result_list = func(obj, grid_2d_radial, *args, **kwargs)
            return grid.structure_2d_list_from_result_list(result_list=result_list)

        if not isinstance(grid, grid_2d_irregular.Grid2DIrregular) and not isinstance(
            grid, grid_2d.Grid2D
        ):
            return func(obj, grid, *args, **kwargs)

    return wrapper


def transform(func):
    """Checks whether the input Grid2D of (y,x) coordinates have previously been transformed. If they have not \
    been transformed then they are transformed.

    Parameters
    ----------
    func : (profile, grid *args, **kwargs) -> Object
        A function where the input grid is the grid whose coordinates are transformed.

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(cls, grid, *args, **kwargs):
        """

        Parameters
        ----------
        cls : Profile
            The class that owns the function.
        grid : grid_like
            The (y, x) coordinates in the original reference frame of the grid.

        Returns
        -------
            A grid_like object whose coordinates may be transformed.
        """

        if not isinstance(
            grid,
            (
                grid_2d.Grid2DTransformed,
                grid_2d.Grid2DTransformedNumpy,
                grid_2d_irregular.Grid2DIrregularTransformed,
            ),
        ):
            result = func(
                cls, cls.transform_grid_to_reference_frame(grid), *args, **kwargs
            )

            return result

        else:
            return func(cls, grid, *args, **kwargs)

    return wrapper


def relocate_to_radial_minimum(func):
    """ Checks whether any coordinates in the grid are radially near (0.0, 0.0), which can lead to numerical faults in \
    the evaluation of a function (e.g. numerical integration reaching a singularity at (0.0, 0.0)). If any coordinates
    are radially within the the radial minimum threshold, their (y,x) coordinates are shifted to that value to ensure
    they are evaluated at that coordinate.

    The value the (y,x) coordinates are rounded to is set in the 'radial_min.ini' config.

    Parameters
    ----------
    func : (profile, *args, **kwargs) -> Object
        A function that takes a grid of coordinates which may have a singularity as (0.0, 0.0)

    Returns
    -------
        A function that can except cartesian or transformed coordinates
    """

    @wraps(func)
    def wrapper(cls, grid, *args, **kwargs):
        """

        Parameters
        ----------
        cls : Profile
            The class that owns the function.
        grid : grid_like
            The (y, x) coordinates which are to be radially moved from (0.0, 0.0).

        Returns
        -------
            The grid_like object whose coordinates are radially moved from (0.0, 0.0).
        """

        grid_radial_minimum = conf.instance["grids"]["radial_minimum"][
            "radial_minimum"
        ][cls.__class__.__name__]

        with np.errstate(all="ignore"):  # Division by zero fixed via isnan

            grid_radii = cls.grid_to_grid_radii(grid=grid)

            grid_radial_scale = np.where(
                grid_radii < grid_radial_minimum, grid_radial_minimum / grid_radii, 1.0
            )
            grid = np.multiply(grid, grid_radial_scale[:, None])
        grid[np.isnan(grid)] = grid_radial_minimum

        return func(cls, grid, *args, **kwargs)

    return wrapper
