"""Tests for EdOps modules."""
from tutor.edops import modules
from tutor.edops.health import HealthCheckType


def test_load_modules():
    """Test that modules can be loaded."""
    all_modules = modules._load_modules()

    assert "base" in all_modules
    assert "common" in all_modules

    # Check base module
    base = all_modules["base"]
    assert base.required is True
    assert base.template == "local/zhjx-base.yml"
    assert base.target == "local/zhjx-base.yml"
    assert len(base.depends_on) == 0

    # Check common module
    common = all_modules["common"]
    assert common.required is True
    assert "base" in common.depends_on


def test_module_health_checks():
    """Test that health checks are properly loaded."""
    all_modules = modules._load_modules()

    # Base should have health checks
    base = all_modules["base"]
    assert len(base.health_checks) > 0

    # Check a specific health check
    nacos_check = None
    for hc in base.health_checks:
        if hc.service == "zhjx-nacos":
            nacos_check = hc
            break

    assert nacos_check is not None
    # 类型应该是 HealthCheckType 枚举，不是字符串
    assert nacos_check.type == HealthCheckType.HTTP
    assert nacos_check.type.value == "http"  # 枚举的值是字符串
    assert nacos_check.timeout == 30


def test_module_images():
    """Test that images are properly loaded."""
    all_modules = modules._load_modules()

    # Common should have images
    common = all_modules["common"]
    assert len(common.images) > 0

    # Check a specific image
    gateway_image = None
    for img in common.images:
        if img.name == "ly-ac-gateway-svc":
            gateway_image = img
            break

    assert gateway_image is not None
    assert "{{EDOPS_IMAGE_REGISTRY}}" in gateway_image.repository
    assert gateway_image.version_var == "EDOPS_VERSION_SVC_DEFAULT"


def test_module_order_resolution():
    """Test that module dependency order is correctly resolved."""
    # This would require a config, which we don't have in unit tests
    # For now, just test that the function exists
    assert hasattr(modules, "_resolve_module_order")


def test_get_enabled_module_targets():
    """Test that the correct module targets are returned."""
    # 1. Test with only default modules (base, common)
    config = {"EDOPS_ENABLED_MODULES": []}
    targets = modules.get_enabled_module_targets(config)
    assert "local/zhjx-base.yml" in targets
    assert "local/zhjx-common.yml" in targets
    assert "local/zhjx-zlmediakit.yml" not in targets

    # 2. Test with an optional module enabled
    config = {"EDOPS_ENABLED_MODULES": ["zhjx_zlmediakit"]}
    targets = modules.get_enabled_module_targets(config)
    assert "local/zhjx-base.yml" in targets
    assert "local/zhjx-common.yml" in targets
    assert "local/zhjx-zlmediakit.yml" in targets


def test_run_flag_synchronization():
    """Test that legacy RUN_* flags are synchronized with EDOPS_ENABLED_MODULES."""
    # 1. Test that the flag is not set by default
    config = {"EDOPS_ENABLED_MODULES": []}
    modules._update_run_flags_from_enabled_modules(config)
    assert config.get("RUN_ZHJX_ZLMEDIAKIT") is None

    # 2. Test that the flag is set when the module is enabled
    config = {"EDOPS_ENABLED_MODULES": ["zhjx_zlmediakit"]}
    modules._update_run_flags_from_enabled_modules(config)
    assert config["RUN_ZHJX_ZLMEDIAKIT"] is True
