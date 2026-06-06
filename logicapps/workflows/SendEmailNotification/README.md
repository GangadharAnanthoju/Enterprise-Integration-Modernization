# SendEmailNotification

## Purpose

Sends an email via the enterprise email service. Use this MCP tool whenever an email notification needs to be delivered to a user, team, or system.

## MCP Metadata

| Field | Value |
|---|---|
| Tool name | `SendEmailNotification` |
| Logic Apps workflow | `SendEmailNotification` |
| Risk level | Medium |
| Approval required | No |
| Required parameters | `to`, `subject`, `body` |

## Parameters

| Parameter | Required | Description |
|---|---:|---|
| `to` | Yes | Recipient email address. |
| `subject` | Yes | Email subject line. |
| `body` | Yes | Email body as plain text or HTML. |
| `cc` | No | CC recipient email address. |
| `body_type` | No | `HTML` or `Text`; defaults to `Text`. |
| `from_name` | No | Display name for the sender. |
| `priority` | No | `High`, `Normal`, or `Low`; defaults to `Normal`. |
| `category` | No | Routing/filtering tag such as `loan`, `invoice`, or `alert`. |

## Response

Returns a confirmation message with the recipient address when the notification is sent successfully.
