# Asset & Maintenance Link (am_asset_maintenance_link)

This module provides a seamless bi-directional integration between Odoo's Accounting Assets (`om_account_asset`) and Maintenance Equipment (`maintenance`).

## Features

1. **1-to-1 Link**: Links each Maintenance Equipment directly to a corresponding Accounting Asset.
2. **Category Mapping**: Link Equipment Categories to Asset Categories for streamlined data entry and categorization.
3. **Auto-Create Assets**: A Server Action in the Equipment list allows for bulk generating Accounting Assets directly from Maintenance records.
4. **Auto-Create Equipment**: When an Accounting Asset is validated, the module can automatically auto-generate its corresponding Maintenance Equipment (controlled by a setting on the Asset Category). 
5. **Auto-linking Accounting Category**: Quickly create and link an Accounting Category directly from an Equipment Category form using the "Create Accounting Category" button.
6. **Bi-directional Name Syncing**: Updating the name of the asset updates the equipment's name, and vice versa. 
7. **Cost Syncing**: The gross value of the Asset automatically synchronizes to the Cost field on the Equipment (with proper Company Currency conversion). The Cost field on the equipment becomes Read-Only when linked to ensure financial integrity.
8. **Lifecycle Protection**:
   - Prevents deletion of an Equipment if it forms part of an active Accounting Asset.
   - Archiving an Equipment will automatically log a warning message on the Chatter of the related Accounting Asset, prompting the accounting team to dispose of or act upon the asset.
   - Enforces Multi-Company constraints. 

## How To Use

### 1. Initial Setup (Category Mapping)
Before bulk syncing your equipments, configure your categories.
- Go to **Maintenance > Configuration > Equipment Categories**.
- Open a category (e.g., *Computers*). 
- In the "Accounting" section, select the corresponding **Accounting Asset Category**.
- If an accounting category doesn't exist, simply click the **"Create Accounting Category"** button. The system will pop up a window to create an Asset Category, auto-filling the name. Once you select the required GL accounts and save, it will automatically link back to this Equipment Category.

### 2. Auto-generating Assets from existing Equipment (Migration/Bulk)
If you already have a list of Maintenance Equipments and want them registered as Accounting Assets:
- Go to **Maintenance > Equipments**.
- Switch to the List view. 
- Select the equipments you wish to migrate using the left checkboxes.
- Click on the **Action** menu (⚙️ Gear icon).
- Select **Create Accounting Asset**. 
- The system will auto-generate Draft Assets with linked Categories, Costs, Dates, and Vendors. Review them in the Accounting app and Validate.

### 3. Auto-generating Equipment from New Assets
If your process starts from Accounting (e.g., Purchasing logs the Asset first):
- Go to **Accounting > Configuration > Asset Models**.
- Open your category and check the **"Auto-create Maintenance Equipment"** box under the Maintenance tab.
- Whenever a new Asset belonging to this category is **Validated**, the system will automatically create the linked Maintenance Equipment, syncing its name, cost, vendor, and date.
 
## Technical Overview (For Developers)

- **Models Extended**: `account.asset.asset`, `account.asset.category`, `maintenance.equipment`, `maintenance.equipment.category`.
- **Dependencies**: `maintenance`, `om_account_asset`.
- **Key Methods Override**:
  - `account.asset.asset.validate()`: Hooked to trigger equipment creation.
  - `write()` & `unlink()`: Overridden on both models to enforce bi-directional sync, prevent infinite recursion, and restrict unauthorized deletion. 
  - `maintenance.equipment`: Extended with `action_generate_asset()` corresponding to the server action UI.
  - `account.asset.category.create()`: Context-aware override to auto-link back to the calling maintenance category. 
