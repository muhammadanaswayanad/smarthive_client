# SmartHive Client Addon

## Overview

SmartHive Client is an Odoo 17 CE addon that enables your instance to be managed remotely by a SmartHive server running on Odoo 18 EE. This allows centralized management, payment monitoring, and access control.

## Features

- **Remote Management**: Receive commands and status updates from SmartHive server
- **Warning Banners**: Display payment reminders and system notifications
- **Access Control**: Block/unblock system access remotely
- **Heartbeat Monitoring**: Regular status reporting to server
- **Secure Communication**: API key based authentication
- **Payment Alerts**: Show outstanding payment information
- **Status Logging**: Track all server communications

## Installation

1. Copy the `smarthive_client` folder to your Odoo 17 addons directory
2. Restart Odoo and update the app list
3. Install the "SmartHive Client" addon from Apps menu
4. Configure connection to SmartHive server

## Configuration

### Initial Setup

1. Go to **SmartHive Client > Configuration**
2. Create a new configuration record with:
   - **Server URL**: Your SmartHive server URL (e.g., `https://server.example.com`)
   - **Client ID**: Unique identifier (must match server configuration)
   - **API Key**: Secure key for authentication (must match server)
   - **Heartbeat Interval**: How often to contact server (default: 15 minutes)

### Server-Side Setup

Ensure the corresponding client record is created on your SmartHive server with:
- Matching Client ID
- Matching API Key
- Your client domain/URL

## Usage

### Automatic Operations

Once configured, the addon will automatically:
- Send heartbeat signals to server every 15 minutes
- Receive and apply server commands (block/unblock, warnings)
- Display warning banners when configured by server
- Log all activities for audit purposes

### Manual Operations

#### Test Connection
- Use "Test Connection" button in configuration to verify server communication

#### Send Heartbeat
- Use "Send Heartbeat" to manually sync with server

#### View Logs
- Check **SmartHive Client > Status Log** for communication history

## Warning System

The addon can display different types of warnings:

### Warning Banner
- Appears at top of all pages when activated by server
- Shows payment reminders and system notices
- Can display outstanding amounts
- Auto-refreshes every minute

### Block Screen
- Full-screen overlay when access is blocked
- Prevents all system interaction except for admins
- Shows block reason and contact information
- Cannot be dismissed by regular users

## Security

### Access Control
- Only administrators can configure SmartHive settings
- Regular users see warnings but cannot modify them
- Blocked users cannot access system (except admins)
- All communications are logged

### API Security
- API key authentication for server communication
- Client ID verification
- HTTPS recommended for secure communication
- Request validation and error handling

## API Endpoints

The addon provides these endpoints for server communication:

- `GET /smarthive_client/ping` - Health check
- `POST /smarthive_client/block` - Block client access
- `POST /smarthive_client/unblock` - Unblock client access  
- `POST /smarthive_client/warning` - Set warning banner
- `GET /smarthive_client/status` - Get current status
- `GET /smarthive_client/warning_data` - Get warning data for UI

## Cron Jobs

### Heartbeat Cron
- **Frequency**: Every 15 minutes (configurable)
- **Purpose**: Send status updates to server
- **Actions**: Reports system health, receives commands

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to SmartHive server
**Solutions**:
1. Verify server URL is correct and accessible
2. Check API key matches server configuration
3. Ensure firewall allows outbound connections
4. Test with "Test Connection" button

### Warnings Not Showing

**Problem**: Warning banners not displaying
**Solutions**:
1. Check if warning is enabled in server
2. Verify heartbeat is working (check logs)
3. Clear browser cache
4. Check for JavaScript errors in console

### Access Still Blocked

**Problem**: Cannot access system after unblock
**Solutions**:
1. Verify server sent unblock command
2. Check status logs for confirmation
3. Clear browser session/cookies
4. Contact server administrator

### Heartbeat Failures

**Problem**: Regular connection failures in logs
**Solutions**:
1. Check server availability
2. Verify API credentials are correct
3. Check network connectivity
4. Increase heartbeat interval if network is unstable

## Status Codes

### Connection Status
- **Success**: Normal operation
- **Warning**: Minor issues, system still functional
- **Error**: Communication failures, may affect functionality

### Block Status
- **Blocked**: Full access restriction in effect
- **Unblocked**: Normal access restored
- **Pending**: Status change in progress

## Development

### Extending the Addon

To add custom functionality:

1. **Custom Warning Types**: Extend the warning banner template
2. **Additional APIs**: Add new endpoints in controllers
3. **Custom Actions**: Override user models for specialized behavior
4. **Enhanced Logging**: Extend status model for detailed tracking

### Testing

Use the built-in test endpoints:
- Manual heartbeat sending
- Connection testing
- Status verification

## Support

For technical support:
1. Check status logs for error details
2. Verify server-side configuration
3. Test network connectivity
4. Review Odoo logs for system errors

For more information, visit: https://www.smarthive.com