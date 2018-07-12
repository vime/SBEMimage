# -*- coding: utf-8 -*-

#==============================================================================
#   SBEMimage, ver. 2.0
#   Acquisition control software for serial block-face electron microscopy
#   (c) 2016-2018 Benjamin Titze,
#   Friedrich Miescher Institute for Biomedical Research, Basel.
#   This software is licensed under the terms of the MIT License.
#   See LICENSE.txt in the project root folder.
#==============================================================================

"""This module manages the grids. It holds all the grid parameters and provides
   getter and setter access to other modules, adds and deletes grids,
   calculates position and focus maps.
"""

import json
import utils


class GridManager(object):

    def __init__(self, config, sem, coordinate_system):
        self.cfg = config
        self.sem = sem
        self.cs = coordinate_system
        self.grid_map_d = []
        self.grid_map_p = []
        self.number_grids = int(self.cfg['grids']['number_grids'])
        self.size = json.loads(self.cfg['grids']['size'])
        self.rotation = json.loads(self.cfg['grids']['rotation'])
        self.overlap = json.loads(self.cfg['grids']['overlap'])
        self.row_shift = json.loads(self.cfg['grids']['row_shift'])
        self.active_tiles = json.loads(self.cfg['grids']['active_tiles'])
        self.number_active_tiles = json.loads(
            self.cfg['grids']['number_active_tiles'])
        self.tile_size_px_py = json.loads(self.cfg['grids']['tile_size_px_py'])
        self.tile_size_selector = json.loads(
            self.cfg['grids']['tile_size_selector'])
        self.pixel_size = json.loads(self.cfg['grids']['pixel_size'])
        self.dwell_time = json.loads(self.cfg['grids']['dwell_time'])
        self.dwell_time_selector = json.loads(
            self.cfg['grids']['dwell_time_selector'])
        self.display_colour = json.loads(self.cfg['grids']['display_colour'])
        self.origin_wd = json.loads(self.cfg['grids']['origin_wd'])
        self.acq_interval = json.loads(self.cfg['grids']['acq_interval'])
        self.acq_interval_offset = json.loads(
            self.cfg['grids']['acq_interval_offset'])
        self.af_tiles = json.loads(self.cfg['grids']['adaptive_focus_tiles'])
        self.af_gradient = json.loads(
            self.cfg['grids']['adaptive_focus_gradient'])
        self.af_active = json.loads(self.cfg['grids']['use_adaptive_focus'])
        self.initialize_all_grid_maps()

    def add_new_grid(self):
        new_grid_number = self.number_grids
        self.set_grid_size(new_grid_number, [5, 5])
        x_pos = utils.fit_in_range(new_grid_number * 40, 0, 400)
        self.cs.set_grid_origin_s(new_grid_number, [x_pos, 0])
        self.set_rotation(new_grid_number, 0)
        self.set_overlap(new_grid_number, 200)
        self.set_row_shift(new_grid_number, 0)
        self.set_number_active_tiles(new_grid_number, 0)
        self.set_active_tiles(new_grid_number, [])
        self.set_tile_size_px_py(new_grid_number, [4096, 3072])
        self.set_tile_size_selector(new_grid_number, 4)
        self.set_pixel_size(new_grid_number, 10)
        self.set_dwell_time(new_grid_number, 0.8)
        self.set_dwell_time_selector(new_grid_number, 4)
        # Choose colour not already used:
        new_colours = [c for c in range(8) if c not in self.display_colour]
        if not new_colours:
            # If all colours have been used already, use 1 (green):
            new_colours = [1]
        self.set_display_colour(new_grid_number, new_colours[0])
        self.set_origin_wd(new_grid_number, 0)
        self.set_acq_interval(new_grid_number, 1)
        self.set_acq_interval_offset(new_grid_number, 0)
        self.set_adaptive_focus_enabled(new_grid_number, False)
        self.set_adaptive_focus_tiles(new_grid_number, [-1, -1, -1])
        self.set_adaptive_focus_gradient(new_grid_number, [0, 0])
        self.grid_map_p.append({})
        self.grid_map_d.append({})
        self.grid_map_p_gaps.append({})
        self.calculate_grid_map(new_grid_number)
        self.number_grids += 1
        self.cfg['grids']['number_grids'] = str(self.number_grids)

    def delete_grid(self):
        # Delete last item from each grid variable:
        self.cs.delete_grid_origin(self.number_grids - 1)
        del self.size[-1]
        self.cfg['grids']['size'] = str(self.size)
        del self.rotation[-1]
        self.cfg['grids']['rotation'] = str(self.rotation)
        del self.overlap[-1]
        self.cfg['grids']['overlap'] = str(self.overlap)
        del self.row_shift[-1]
        self.cfg['grids']['row_shift'] = str(self.row_shift)
        del self.active_tiles[-1]
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        del self.number_active_tiles[-1]
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)
        del self.tile_size_px_py[-1]
        self.cfg['grids']['tile_size_px_py'] = str(self.tile_size_px_py)
        del self.tile_size_selector[-1]
        self.cfg['grids']['tile_size_selector'] = str(self.tile_size_selector)
        del self.pixel_size[-1]
        self.cfg['grids']['pixel_size'] = str(self.pixel_size)
        del self.dwell_time[-1]
        self.cfg['grids']['dwell_time'] = str(self.dwell_time)
        del self.dwell_time_selector[-1]
        self.cfg['grids']['dwell_time_selector'] = str(
            self.dwell_time_selector)
        del self.display_colour[-1]
        self.cfg['grids']['display_colour'] = str(self.display_colour)
        del self.origin_wd[-1]
        self.cfg['grids']['origin_wd'] = str(self.origin_wd)
        del self.acq_interval[-1]
        self.cfg['grids']['acq_interval'] = str(self.acq_interval)
        del self.acq_interval_offset[-1]
        self.cfg['grids']['acq_interval_offset'] = str(self.acq_interval_offset)
        del self.af_tiles[-1]
        self.cfg['grids']['adaptive_focus_tiles'] = str(self.af_tiles)
        del self.af_gradient[-1]
        self.cfg['grids']['adaptive_focus_gradient'] = str(self.af_gradient)
        del self.af_active[-1]
        self.cfg['grids']['use_adaptive_focus'] = str(self.af_active)
        # Number of grids:
        self.number_grids -= 1
        self.cfg['grids']['number_grids'] = str(self.number_grids)

    def get_number_grids(self):
        return self.number_grids

    def get_grid_size(self, grid_number):
        return self.size[grid_number]

    def get_grid_size_px_py(self, grid_number):
        cols = self.size[grid_number][1]
        width = (cols * self.tile_size_px_py[grid_number][0]
                 - (cols - 1) * self.overlap[grid_number]
                 + self.row_shift[grid_number])
        rows = self.size[grid_number][0]
        height = (rows * self.tile_size_px_py[grid_number][1]
                 - (rows - 1) * self.overlap[grid_number])
        return width, height

    def set_grid_size(self, grid_number, size):
        if grid_number < len(self.size):
            if self.size[grid_number] != list(size):
                self.update_active_tiles_to_new_grid_size(
                    grid_number, list(size))
                self.size[grid_number] = list(size)
        else:
            self.size.append(list(size))
        self.cfg['grids']['size'] = str(self.size)

    def get_number_rows(self, grid_number):
        return self.size[grid_number][0]

    def get_number_cols(self, grid_number):
        return self.size[grid_number][1]

    def get_number_tiles(self, grid_number):
        return self.size[grid_number][0] * self.size[grid_number][1]

    def get_rotation(self, grid_number):
        return self.rotation[grid_number]

    def set_rotation(self, grid_number, rotation):
        if grid_number < len(self.rotation):
            self.rotation[grid_number] = rotation
        else:
            self.rotation.append(rotation)
        self.cfg['grids']['rotation'] = str(self.rotation)

    def get_display_colour(self, grid_number):
        return utils.COLOUR_SELECTOR[self.display_colour[grid_number]]

    def get_display_colour_index(self, grid_number):
        return self.display_colour[grid_number]

    def set_display_colour(self, grid_number, colour):
        if grid_number < len(self.display_colour):
            self.display_colour[grid_number] = colour
        else:
            self.display_colour.append(colour)
        self.cfg['grids']['display_colour'] = str(self.display_colour)

    def get_overlap(self, grid_number):
        return self.overlap[grid_number]

    def set_overlap(self, grid_number, overlap):
        if grid_number < len(self.overlap):
            self.overlap[grid_number] = overlap
        else:
            self.overlap.append(overlap)
        self.cfg['grids']['overlap'] = str(self.overlap)

    def get_row_shift(self, grid_number):
        return self.row_shift[grid_number]

    def set_row_shift(self, grid_number, row_shift):
        if grid_number < len(self.row_shift):
            self.row_shift[grid_number] = row_shift
        else:
            self.row_shift.append(row_shift)
        self.cfg['grids']['row_shift'] = str(self.row_shift)

    def get_tile_size_px_py(self, grid_number):
        return self.tile_size_px_py[grid_number]

    def get_tile_size_selector(self, grid_number):
        return self.tile_size_selector[grid_number]

    def set_tile_size_selector(self, grid_number, selector):
        if grid_number < len(self.tile_size_selector):
            self.tile_size_selector[grid_number] = selector
        else:
            self.tile_size_selector.append(selector)
        self.cfg['grids']['tile_size_selector'] = str(self.tile_size_selector)
        # Update explicit storage of frame size:
        if grid_number < len(self.tile_size_px_py):
            self.tile_size_px_py[grid_number] = self.sem.STORE_RES[selector]
        else:
            self.tile_size_px_py.append(self.sem.STORE_RES[selector])
        self.cfg['grids']['tile_size_px_py'] = str(self.tile_size_px_py)

    def get_tile_width_p(self, grid_number):
        return self.tile_size_px_py[grid_number][0]

    def get_tile_height_p(self, grid_number):
        return self.tile_size_px_py[grid_number][1]

    def get_tile_width_d(self, grid_number):
        return (self.tile_size_px_py[grid_number][0]
                * self.pixel_size[grid_number] / 1000)

    def get_tile_height_d(self, grid_number):
        return (self.tile_size_px_py[grid_number][1]
                * self.pixel_size[grid_number] / 1000)

    def set_tile_size_px_py(self, grid_number, tile_size_px_py):
        if grid_number < len(self.tile_size_px_py):
            self.tile_size_px_py[grid_number] = tile_size_px_py
        else:
            self.tile_size_px_py.append(tile_size_px_py)
        self.cfg['grids']['tile_size_px_py'] = str(self.tile_size_px_py)

    def get_tile_position_d(self, grid_number, tile_number):
        return (self.grid_map_d[grid_number][tile_number][0],
                self.grid_map_d[grid_number][tile_number][1])

    def get_pixel_size(self, grid_number):
        return self.pixel_size[grid_number]

    def get_pixel_size_list(self):
        return self.pixel_size

    def set_pixel_size(self, grid_number, pixel_size):
        if grid_number < self.number_grids:
            self.pixel_size[grid_number] = pixel_size
        else:
            self.pixel_size.append(pixel_size)
        self.cfg['grids']['pixel_size'] = str(self.pixel_size)

    def get_dwell_time(self, grid_number):
        return self.dwell_time[grid_number]

    def get_dwell_time_list(self):
        return self.dwell_time

    def set_dwell_time(self, grid_number, dwell_time):
        if grid_number < len(self.dwell_time):
            self.dwell_time[grid_number] = dwell_time
        else:
            self.dwell_time.append(dwell_time)
        self.cfg['grids']['dwell_time'] = str(self.dwell_time)

    def get_dwell_time_selector(self, grid_number):
        return self.dwell_time_selector[grid_number]

    def set_dwell_time_selector(self, grid_number, selector):
        if grid_number < len(self.dwell_time_selector):
            self.dwell_time_selector[grid_number] = selector
        else:
            self.dwell_time_selector.append(selector)
        self.cfg['grids']['dwell_time_selector'] = str(
            self.dwell_time_selector)
        # Update explict storage of dwell times:
        if grid_number < len(self.dwell_time):
            self.dwell_time[grid_number] = self.sem.DWELL_TIME[selector]
        else:
            self.dwell_time.append(self.sem.DWELL_TIME[selector])
        self.cfg['grids']['dwell_time'] = str(self.dwell_time)

    def get_origin_wd(self, grid_number):
        return self.origin_wd[grid_number]

    def set_origin_wd(self, grid_number, origin_wd):
        if grid_number < len(self.origin_wd):
            self.origin_wd[grid_number] = origin_wd
        else:
            self.origin_wd.append(origin_wd)
        self.cfg['grids']['origin_wd'] = str(self.origin_wd)

    def get_tile_wd(self, grid_number, tilenumber):
        return(self.grid_map_d[grid_number][tilenumber][3])

    def set_tile_wd(self, grid_number, tile_number, wd):
        if grid_number < len(self.grid_map_d):
            self.grid_map_d[grid_number][tile_number][3] = wd

    def get_active_tiles(self, grid_number):
        if grid_number is not None and grid_number < self.number_grids:
            return self.active_tiles[grid_number]
        else:
            return []

    def get_number_active_tiles(self, grid_number):
        return self.number_active_tiles[grid_number]

    def get_total_number_active_tiles(self):
        # Count all active tiles across all grids:
        sum_active_tiles = 0
        for grid_number in range(self.number_grids):
            sum_active_tiles += self.number_active_tiles[grid_number]
        return sum_active_tiles

    def set_active_tiles(self, grid_number, active_tiles):
        if grid_number < len(self.active_tiles):
            self.active_tiles[grid_number] = active_tiles
        else:
            self.active_tiles.append(active_tiles)
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)

    def set_number_active_tiles(self, grid_number, number):
        if grid_number < len(self.number_active_tiles):
            self.number_active_tiles[grid_number] = number
        else:
            self.number_active_tiles.append(number)
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def get_active_tile_str_list(self, grid_number):
        return ['Tile %d' % t for t in self.active_tiles[grid_number]]

    def get_tile_str_list(self, grid_number):
        return ['Tile %d' % t
                for t in range(0, self.get_number_tiles(grid_number))]

    def get_grid_str_list(self):
        return ['Grid %d' % g
                for g in range(0, self.number_grids)]

    def get_acq_interval(self, grid_number):
        return self.acq_interval[grid_number]

    def set_acq_interval(self, grid_number, interval):
        if grid_number < len(self.acq_interval):
            self.acq_interval[grid_number] = interval
        else:
            self.acq_interval.append(interval)
        self.cfg['grids']['acq_interval'] = str(self.acq_interval)

    def get_acq_interval_offset(self, grid_number):
        return self.acq_interval_offset[grid_number]

    def set_acq_interval_offset(self, grid_number, offset):
        if grid_number < len(self.acq_interval_offset):
            self.acq_interval_offset[grid_number] = offset
        else:
            self.acq_interval_offset.append(offset)
        self.cfg['grids']['acq_interval_offset'] = str(
            self.acq_interval_offset)

    def is_intervallic_acq_active(self):
        sum_intervals = 0
        for grid_number in range(self.number_grids):
            sum_intervals += self.acq_interval[grid_number]
        if sum_intervals > self.number_grids:
            return True
        else:
            return False

    def is_slice_active(self, grid_number, slice_counter):
        offset = self.acq_interval_offset[grid_number]
        if slice_counter >= offset:
            is_active = (slice_counter - offset) % self.acq_interval[grid_number] == 0
        else:
            is_active = False
        return is_active

    def get_tile_cycle_time(self, grid_number):
        # Calculate cycle time from SmartSEM data:
        size_selector = self.tile_size_selector[grid_number]
        scan_speed = self.sem.DWELL_TIME.index(self.dwell_time[grid_number])
        return (self.sem.CYCLE_TIME[size_selector][scan_speed] + 0.2)

    def get_adaptive_focus_tiles(self, grid_number):
        return self.af_tiles[grid_number]

    def set_adaptive_focus_tiles(self, grid_number, af_tiles):
        if grid_number < len(self.af_tiles):
            self.af_tiles[grid_number] = af_tiles
        else:
            self.af_tiles.append(af_tiles)
        self.cfg['grids']['adaptive_focus_tiles'] = str(self.af_tiles)

    def get_adaptive_focus_gradient(self, grid_number):
        return self.af_gradient[grid_number]

    def set_adaptive_focus_gradient(self, grid_number, af_gradient):
        if grid_number < len(self.af_gradient):
            self.af_gradient[grid_number] = af_gradient
        else:
            self.af_gradient.append(af_gradient)
        self.cfg['grids']['adaptive_focus_gradient'] = str(self.af_gradient)

    def is_adaptive_focus_active(self, grid_number=-1):
        if grid_number == -1:
            sum_af_active = 0
            for grid_number in range(self.number_grids):
                sum_af_active += self.af_active[grid_number]
            if sum_af_active > 0:
                return True
            else:
                return False
        else:
            return (self.af_active[grid_number] == 1)

    def set_adaptive_focus_enabled(self, grid_number, status_enabled):
        if grid_number == len(self.af_active):
            self.af_active.append(0)
        if status_enabled:
            self.af_active[grid_number] = 1
        else:
            self.af_active[grid_number] = 0
        self.cfg['grids']['use_adaptive_focus'] = str(self.af_active)

    def get_af_tile_str_list(self, grid_number):
        return ['Tile %d' % t for t in self.af_tiles[grid_number]]

    def update_active_tiles_to_new_grid_size(self, grid_number, new_size):
        current_rows, current_cols = self.size[grid_number]
        new_rows, new_cols = new_size
        new_active_tiles = []
        # Calculate new active tiles or delete active tiles if no longer in grid:
        for tile_number in self.active_tiles[grid_number]:
            # Calculate coordinate in grid of current size:
            x_pos = tile_number % current_cols
            y_pos = tile_number // current_cols
            # Calculate tile number in new grid:
            if (x_pos < new_cols) and (y_pos < new_rows):
                new_tile_number = x_pos + y_pos * new_cols
                new_active_tiles.append(new_tile_number)
        # Save new active tiles:
        self.active_tiles[grid_number] = new_active_tiles
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        self.number_active_tiles[grid_number] = len(new_active_tiles)
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def calculate_grid_map(self, grid_number):
        # Calculating tile positions in SEM coordinates, unit: micrometres
        rows, cols = self.size[grid_number]
        width_p, height_p = self.tile_size_px_py[grid_number]
        pixel_size = self.pixel_size[grid_number]
        overlap = self.overlap[grid_number]
        row_shift = self.row_shift[grid_number]

        for y_pos in range(rows):
            for x_pos in range(cols):
                tile_number = x_pos + y_pos * cols
                x_coord = x_pos * (width_p - overlap)
                y_coord = y_pos * (height_p - overlap)
                # Introduce alternating shift in x direction
                # to avoid quadruple beam exposure:
                x_shift = row_shift * (y_pos % 2)
                # Save position in tile map
                # Format of pixel grid map:
                # 0: x-coordinate, 1: y-coordinate
                self.grid_map_p[grid_number][tile_number] = [
                    x_coord + x_shift,
                    y_coord]
                # Format of SEM coordinate grid map:
                # 0: X-coord, 1: Y-coord,
                # 2: active/inactive (True/False), 3: working distance
                wd_delta_x, wd_delta_y = self.af_gradient[grid_number]
                self.grid_map_d[grid_number][tile_number] = [
                    (x_coord + x_shift) * pixel_size / 1000,       # x
                    y_coord * pixel_size / 1000,                   # y
                    tile_number in self.active_tiles[grid_number], # tile active?
                    self.origin_wd[grid_number]
                    + x_pos * wd_delta_x
                    + y_pos * wd_delta_y]                          # wd

    def initialize_all_grid_maps(self):
        # Inititalize data structures:
        self.grid_map_d = [{} for i in range(self.number_grids)]
        self.grid_map_p = [{} for i in range(self.number_grids)]
        self.grid_map_p_gaps = [{} for i in range(self.number_grids)]
        for grid_number in range(self.number_grids):
            self.calculate_grid_map(grid_number)

    def adjust_focus_map(self, grid_number, diff):
        self.af_tiles[grid_number][0] += diff
        self.af_tiles[grid_number][1] += diff
        self.af_tiles[grid_number][2] += diff
        self.cfg['grids']['adaptive_focus_tiles'] = str(self.af_tiles)
        self.calculate_focus_map(grid_number)

    def calculate_focus_map(self, grid_number):
        success = True
        af_tiles = self.af_tiles[grid_number]
        if af_tiles[0] >= 0:
            row_length = self.size[grid_number][1]
            row0 = af_tiles[0] // row_length
            row1 = af_tiles[1] // row_length
            # Tile1 must be right of Tile0 and in the same row:
            if (af_tiles[1] > af_tiles[0]) and (row0 == row1):
                x_diff = af_tiles[1] - af_tiles[0]
                wd_delta_x = (
                    self.grid_map_d[grid_number][af_tiles[1]][3]
                    - self.grid_map_d[grid_number][af_tiles[0]][3])/x_diff
            else:
                success = False
            # Tile3 must be below Tile0 and in the same column:
            col0 = af_tiles[0] % row_length
            col2 = af_tiles[2] % row_length
            if (af_tiles[2] > af_tiles[0]) and (col0 == col2):
                y_diff = (af_tiles[2] - af_tiles[0]) // row_length
                wd_delta_y = (
                    self.grid_map_d[grid_number][af_tiles[2]][3]
                    - self.grid_map_d[grid_number][af_tiles[0]][3])/y_diff
            else:
                success = False

            if success:
                self.af_gradient[grid_number] = [wd_delta_x, wd_delta_y]
                self.cfg['grids']['adaptive_focus_gradient'] = str(
                    self.af_gradient)
                # Calculate wd at the origin of the tiling:
                x_diff_origin = af_tiles[0] % row_length
                y_diff_origin = af_tiles[0] // row_length
                self.origin_wd[grid_number] = (
                      self.grid_map_d[grid_number][af_tiles[0]][3]
                      - (x_diff_origin * wd_delta_x)
                      - (y_diff_origin * wd_delta_y))
                self.cfg['grids']['origin_wd'] = str(self.origin_wd)

                # Update wd for full grid:
                for y_pos in range(0, self.size[grid_number][0]):
                    for x_pos in range(0, self.size[grid_number][1]):
                        tile_number = y_pos * row_length + x_pos
                        self.grid_map_d[grid_number][tile_number][3] = (
                                self.origin_wd[grid_number]
                                + x_pos * wd_delta_x
                                + y_pos * wd_delta_y)
        else:
            success = False
        return success

    def get_gapped_grid_map(self, grid_number):
        for y_pos in range(0, self.size[grid_number][0]):
            for x_pos in range(0, self.size[grid_number][1]):
                tile_number = x_pos + y_pos * self.size[grid_number][1]
                x_coord = x_pos * 1.05 * self.tile_size_px_py[grid_number][0]
                y_coord = y_pos * 1.05 * self.tile_size_px_py[grid_number][1]
                # Introduce alternating shift in x direction
                # to avoid quadruple beam exposure:
                x_shift = self.row_shift[grid_number] * (y_pos % 2)
                # Save position in tile map
                # Format of each entry: X-coord, Y-coord, bool (active: 1, inactive: 0)
                self.grid_map_p_gaps[grid_number][tile_number] = [
                    (x_coord + x_shift) * self.pixel_size[grid_number] / 1000,
                    y_coord * self.pixel_size[grid_number] / 1000]
        return self.grid_map_p_gaps[grid_number]

    def save_grid_setup(self, timestamp):
        # This assumes that base directory and logs subdirectory have already been created
        file_name = self.cfg['acq']['base_dir'] + '/meta/logs/' + \
                    'gridmap_' + timestamp + '.txt'
        grid_map_file = open(file_name, 'w')
        for i in range(0, self.number_grids):
            for t in range(0, self.size[i][0] * self.size[i][1]):
                grid_map_file.write(str(i) + '.' + str(t) + ';' +
                                    str(self.grid_map_p[i][t][0]) + ';' +
                                    str(self.grid_map_p[i][t][1]) + ';' +
                                    str(self.grid_map_d[i][t][2]) + ';' +
                                    str(self.grid_map_d[i][t][3]) + '\n')
        grid_map_file.close()
        return file_name

    def sort_acq_order(self, grid_number):
        # Use snake pattern to minimize number of long motor moves:
        rows = self.size[grid_number][0]
        cols = self.size[grid_number][1]
        ordered_active_tiles = []

        for row_pos in range(rows):
            if (row_pos % 2 == 0):
                start_col, end_col, step = 0, cols, 1
            else:
                start_col, end_col, step = cols-1, -1, -1
            for col_pos in range(start_col, end_col, step):
                tile_number = row_pos * cols + col_pos
                if tile_number in self.active_tiles[grid_number]:
                    ordered_active_tiles.append(tile_number)

        self.active_tiles[grid_number] = ordered_active_tiles

    def select_tile(self, grid_number, tile_number):
        self.grid_map_d[grid_number][tile_number][2] = True
        self.active_tiles[grid_number].append(tile_number)
        self.number_active_tiles[grid_number] += 1
        self.sort_acq_order(grid_number)
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def deselect_tile(self, grid_number, tile_number):
        self.grid_map_d[grid_number][tile_number][2] = False
        self.active_tiles[grid_number].remove(tile_number)
        self.number_active_tiles[grid_number] -= 1
        self.sort_acq_order(grid_number)
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def toggle_tile(self, grid_number, tile_number):
        if self.grid_map_d[grid_number][tile_number][2]:
            self.deselect_tile(grid_number, tile_number)
            text = ' deselected.'
        else:
            self.select_tile(grid_number, tile_number)
            text = ' selected.'
        return 'CTRL: Tile ' + str(grid_number) + '.' + str(tile_number) + text

    def get_tile_coordinates_relative_d(self, grid_number, tile_number):
        # Tile position in SEM coordinates relative to grid origin:
        return (self.grid_map_d[grid_number][tile_number][0],
                self.grid_map_d[grid_number][tile_number][1])

    def get_tile_coordinates_s(self, grid_number, tile_number):
        sx_sy = self.cs.convert_to_s((
            self.grid_map_d[grid_number][tile_number][0],
            self.grid_map_d[grid_number][tile_number][1]))
        return self.cs.add_grid_origin_s(grid_number, sx_sy)

    def get_tile_coordinates_relative_p(self, grid_number, tile_number):
        # Tile position in SEM pixel coordinates relative to grid origin:
        return (self.grid_map_p[grid_number][tile_number][0],
                self.grid_map_p[grid_number][tile_number][1])

    def get_tile_coordinates_p(self, grid_number, tile_number):
        origin_px, origin_py = self.cs.get_grid_origin_p(grid_number)
        return (origin_px + self.grid_map_p[grid_number][tile_number][0],
                origin_py + self.grid_map_p[grid_number][tile_number][1])

    def get_grid_map_d(self, grid_number):
        return self.grid_map_d[grid_number]

    def get_grid_map_p(self, grid_number):
        return self.grid_map_p[grid_number]

    def reset_active_tiles(self, grid_number):
        self.active_tiles[grid_number] = []
        for i in range(self.size[grid_number][0] * self.size[grid_number][1]):
            self.grid_map_d[grid_number][i][2] = False
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        self.number_active_tiles[grid_number] = 0
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def select_all_tiles(self, grid_number):
        self.active_tiles[grid_number] = []
        for i in range(self.size[grid_number][0] * self.size[grid_number][1]):
            self.active_tiles[grid_number].append(i)
            self.grid_map_d[grid_number][i][2] = True
        self.sort_acq_order(grid_number)
        self.cfg['grids']['active_tiles'] = str(self.active_tiles)
        self.number_active_tiles[grid_number] = len(
            self.active_tiles[grid_number])
        self.cfg['grids']['number_active_tiles'] = str(
            self.number_active_tiles)

    def get_tile_bounding_box(self, grid_number, tile_number):
        origin_dx, origin_dy = self.cs.get_grid_origin_d(grid_number)
        top_left_dx = (origin_dx
                      + self.grid_map_d[grid_number][tile_number][0]
                      - self.get_tile_width_d(grid_number)/2)
        top_left_dy = (origin_dy
                      + self.grid_map_d[grid_number][tile_number][1]
                      - self.get_tile_height_d(grid_number)/2)
        bottom_right_dx = top_left_dx + self.get_tile_width_d(grid_number)
        bottom_right_dy = top_left_dy + self.get_tile_height_d(grid_number)
        return (top_left_dx, top_left_dy, bottom_right_dx, bottom_right_dy)
