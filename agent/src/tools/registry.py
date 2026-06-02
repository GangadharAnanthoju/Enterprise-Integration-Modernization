"""Static catalog of approved enterprise MCP tools."""

from tools.contracts import RiskLevel, ToolContract


# Approved enterprise MCP tool catalog. The agent can choose from this list,
# but it must not invent tools outside this registry.
TOOL_REGISTRY: dict[str, ToolContract] = {
    "getOrderStatus": ToolContract(
        name="getOrderStatus",
        description="Look up order status and fulfillment state.",
        business_domain="Order Management",
        backend_system="ERP order service",
        risk_level=RiskLevel.LOW,
        approval_required=False,
        owner="Integration Platform Team",
        version="1.0.0",
        operational_impact="Read-only order lookup.",
        required_entities=("order_id",),
        input_schema_ref="logicapps/workflows/getOrderStatus/sample-request.json",
        output_schema_ref="logicapps/workflows/getOrderStatus/sample-response.json",
    ),
    "validateInvoice": ToolContract(
        name="validateInvoice",
        description="Validate invoice fields and business rules before payment processing.",
        business_domain="Finance",
        backend_system="Invoice validation service",
        risk_level=RiskLevel.MEDIUM,
        approval_required=False,
        owner="Finance Integration Team",
        version="1.0.0",
        operational_impact="Validation-only workflow; no payment action.",
        required_entities=("invoice_id",),
        input_schema_ref="logicapps/workflows/validateInvoice/sample-request.json",
        output_schema_ref="logicapps/workflows/validateInvoice/sample-response.json",
    ),
    "checkShipmentStatus": ToolContract(
        name="checkShipmentStatus",
        description="Retrieve shipment status and delivery exceptions.",
        business_domain="Logistics",
        backend_system="Shipment tracking service",
        risk_level=RiskLevel.LOW,
        approval_required=False,
        owner="Logistics Integration Team",
        version="1.0.0",
        operational_impact="Read-only shipment lookup.",
        required_entities=("shipment_id",),
        input_schema_ref="logicapps/workflows/checkShipmentStatus/sample-request.json",
        output_schema_ref="logicapps/workflows/checkShipmentStatus/sample-response.json",
    ),
    "sendSupplierNotification": ToolContract(
        name="sendSupplierNotification",
        description="Send a supplier-facing notification for an approved business event.",
        business_domain="Supplier Management",
        backend_system="Supplier notification service",
        risk_level=RiskLevel.HIGH,
        approval_required=True,
        owner="Supplier Integration Team",
        version="1.0.0",
        operational_impact="External communication to supplier.",
        required_entities=("shipment_id",),
        input_schema_ref="logicapps/workflows/sendSupplierNotification/sample-request.json",
        output_schema_ref="logicapps/workflows/sendSupplierNotification/sample-response.json",
    ),
    "createApprovalRequest": ToolContract(
        name="createApprovalRequest",
        description="Create a human approval task for a governed workflow.",
        business_domain="Governance",
        backend_system="Approval workflow service",
        risk_level=RiskLevel.MEDIUM,
        approval_required=False,
        owner="Integration Governance Team",
        version="1.0.0",
        operational_impact="Creates an approval task; does not complete the target action.",
        required_entities=(),
        input_schema_ref="logicapps/workflows/createApprovalRequest/sample-request.json",
        output_schema_ref="logicapps/workflows/createApprovalRequest/sample-response.json",
    ),
    "createServiceNowTicket": ToolContract(
        name="createServiceNowTicket",
        description="Create an operational support ticket for an integration incident.",
        business_domain="IT Service Management",
        backend_system="ServiceNow",
        risk_level=RiskLevel.HIGH,
        approval_required=True,
        owner="ITSM Integration Team",
        version="1.0.0",
        operational_impact="Creates a support ticket visible to operations teams.",
        required_entities=(),
        input_schema_ref="logicapps/workflows/createServiceNowTicket/sample-request.json",
        output_schema_ref="logicapps/workflows/createServiceNowTicket/sample-response.json",
    ),
    "queryIntegrationRunStatus": ToolContract(
        name="queryIntegrationRunStatus",
        description="Troubleshoot integration run status by correlation ID.",
        business_domain="Operations",
        backend_system="Application Insights and Log Analytics",
        risk_level=RiskLevel.LOW,
        approval_required=False,
        owner="Integration Operations Team",
        version="1.0.0",
        operational_impact="Read-only operational lookup.",
        required_entities=("correlation_id",),
        input_schema_ref="logicapps/workflows/queryIntegrationRunStatus/sample-request.json",
        output_schema_ref="logicapps/workflows/queryIntegrationRunStatus/sample-response.json",
    ),
}


def list_tools() -> list[ToolContract]:
    """Return approved tools sorted by name for stable API responses and tests."""

    # Sorting keeps API responses predictable for tests, demos, and documentation.
    return [TOOL_REGISTRY[name] for name in sorted(TOOL_REGISTRY)]


def get_tool(tool_name: str) -> ToolContract | None:
    """Return one tool contract by exact MCP tool name."""

    return TOOL_REGISTRY.get(tool_name)


def require_tool(tool_name: str) -> ToolContract:
    """Return one tool contract or raise a clear error for unsupported tools."""

    tool = get_tool(tool_name)
    if tool is None:
        # A missing tool is a governance failure, not a normal empty response.
        raise KeyError(f"Unsupported MCP tool: {tool_name}")
    return tool
