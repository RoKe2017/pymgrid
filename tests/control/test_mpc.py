import numpy as np

from tests.helpers.test_case import TestCase
from tests.helpers.modular_microgrid import get_modular_microgrid

from pymgrid.algos import ModelPredictiveControl


class TestMPC(TestCase):
    def test_init(self):
        microgrid = get_modular_microgrid()
        mpc = ModelPredictiveControl(microgrid)
        self.assertTrue(mpc.is_modular)
        self.assertEqual(mpc.horizon, 1)

    def test_run_with_load_pv_battery_grid(self):
        from pymgrid.microgrid.modules import RenewableModule, LoadModule

        forecast_steps = 10
        pv_const = 50
        load_const = 60
        pv = RenewableModule(time_series=pv_const*np.ones(100))
        load = LoadModule(time_series=load_const*np.ones(100),
                          loss_load_cost=10)

        microgrid = get_modular_microgrid(remove_modules=["pv", "load", "genset"], additional_modules=[pv, load])

        mpc = ModelPredictiveControl(microgrid)
        mpc_output = mpc.run_mpc_on_microgrid(forecast_steps=forecast_steps)
        self.assertEqual(mpc_output.shape[0], forecast_steps)
        self.assertEqual(mpc_output[("grid", 0, "grid_import")].values,
                         [load_const - pv_const] * mpc_output.shape[0] -
                        mpc_output[("battery", 0, "discharge_amount")].values)

    def test_run_with_load_pv_battery_genset(self):
        from pymgrid.microgrid.modules import RenewableModule, LoadModule

        forecast_steps = 10
        pv_const = 50
        load_const = 60
        pv = RenewableModule(time_series=pv_const*np.ones(100))
        load = LoadModule(time_series=load_const*np.ones(100),
                          loss_load_cost=10)

        microgrid = get_modular_microgrid(remove_modules=["pv", "load", "grid"], additional_modules=[pv, load])

        mpc = ModelPredictiveControl(microgrid)
        mpc_output = mpc.run_mpc_on_microgrid(forecast_steps=forecast_steps)
        self.assertEqual(mpc_output.shape[0], forecast_steps)

        self.assertEqual(mpc_output[("load", 0, "load_met")].values, [60.]*mpc_output.shape[0])
        self.assertEqual(mpc_output[("genset", 0, "genset_production")].values, [10.]*mpc_output.shape[0])

    def test_run_twice_with_load_pv_battery_genset(self):
        from pymgrid.microgrid.modules import RenewableModule, LoadModule

        forecast_steps = 10
        pv_const = 50
        load_const = 60
        pv = RenewableModule(time_series=pv_const*np.ones(100))
        load = LoadModule(time_series=load_const*np.ones(100),
                          loss_load_cost=10)

        microgrid = get_modular_microgrid(remove_modules=["pv", "load", "grid"], additional_modules=[pv, load])

        mpc = ModelPredictiveControl(microgrid)
        mpc_output = mpc.run_mpc_on_microgrid(forecast_steps=forecast_steps)

        self.assertEqual(mpc_output.shape[0], forecast_steps)
        self.assertEqual(mpc_output[("load", 0, "load_met")].values, [60.] * mpc_output.shape[0])
        self.assertEqual(mpc_output[("genset", 0, "genset_production")].values, [10.] * mpc_output.shape[0])

        mpc_output = mpc.run_mpc_on_microgrid(forecast_steps=forecast_steps)
        self.assertEqual(mpc_output.shape[0], forecast_steps)
        self.assertEqual(mpc_output[("load", 0, "load_met")].values, [60.] * mpc_output.shape[0])
        self.assertEqual(mpc_output[("genset", 0, "genset_production")].values, [10.] * mpc_output.shape[0])

    def test_run_with_load_pv_battery_grid_different_names(self):
        from pymgrid.microgrid.modules import RenewableModule, LoadModule

        forecast_steps = 10
        pv_const = 50
        load_const = 60
        pv = RenewableModule(time_series=pv_const*np.ones(100))
        load = LoadModule(time_series=load_const*np.ones(100),
                          loss_load_cost=10)

        microgrid = get_modular_microgrid(remove_modules=["pv", "load", "genset"],
                                          additional_modules=[("pv_with_name", pv), ("load_with_name", load)])

        mpc = ModelPredictiveControl(microgrid)
        mpc_output = mpc.run_mpc_on_microgrid(forecast_steps=forecast_steps)
        self.assertEqual(mpc_output.shape[0], forecast_steps)
        self.assertEqual(mpc_output[("load_with_name", 0, "load_met")].values, [load_const]*mpc_output.shape[0])
        self.assertEqual(mpc_output[("grid", 0, "grid_import")].values,
                         [load_const-pv_const]*mpc_output.shape[0]-mpc_output[("battery", 0, "discharge_amount")].values)
        self.assertEqual(mpc_output[("load_with_name", 0, "load_met")].values, [load_const]*mpc_output.shape[0])