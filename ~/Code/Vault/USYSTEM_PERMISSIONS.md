# Permission Matrix

Role-based access control for uCode1 resources

## admin

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✓ | ✓ | ✓ |
| commands | ✓ | ✓ | ✓ | ✓ | ✓ |
| system | ✓ | ✓ | ✓ | ✓ | ✓ |

## user

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✗ | ✓ | ✗ |
| commands | ✓ | ✗ | ✗ | ✓ | ✗ |
| system | ✓ | ✗ | ✗ | ✗ | ✗ |

## guest

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✗ | ✗ | ✗ | ✗ |
| commands | ✓ | ✗ | ✗ | ✓ | ✗ |
| system | ✗ | ✗ | ✗ | ✗ | ✗ |

## developer

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✓ | ✓ | ✗ |
| commands | ✓ | ✓ | ✗ | ✓ | ✗ |
| system | ✓ | ✓ | ✗ | ✓ | ✗ |
