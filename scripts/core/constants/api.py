prefix = "/ppm/api/v1.0"


class DefaultAPI:
    prefix = "/custom_app"
    load_styles = "/load_styles"
    load_file = "/load_file"
    load_configuration = "/load_configuration"


class CommonAPI:
    prefix = f"{prefix}/common"
    get_project_configurations = "/project_config"


class CoreAPI:
    prefix = "/ilens_api/ilens_config"
    stepper_json = f"{prefix}/get_stepper_json"


class DashboardAPI:
    prefix = "/dashboard"
    get_process_order = "/get_process_order"

class CalculationCycleAPIs:
    get_po = "/get_po"
    calculation_cycle_dropdown = "/calculation_cycle_dropdown"
