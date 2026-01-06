# News Fragments

This folder contains changelog fragments for the next release.

## Fragment Types

Create files with the following extensions to categorize changes:

- **`.feature`** - New features and functionality
- **`.bugfix`** - Bug fixes
- **`.doc`** - Documentation changes
- **`.removal`** - Deprecations and removals
- **`.misc`** - Miscellaneous changes

## Usage

1. Create a new file in this folder with a descriptive name and appropriate extension:
   ```
   add-authentication.feature
   fix-database-connection.bugfix
   update-readme.doc
   ```

2. Add a brief description of the change inside the file:
   ```
   Added OAuth2 authentication support
   ```

3. When you run `npm run release`, all fragments will be compiled into CHANGELOG.md and removed.

## Example

```bash
echo "Added user profile endpoint" > fragments/user-profile.feature
echo "Fixed database connection pool exhaustion" > fragments/db-pool.bugfix
```
