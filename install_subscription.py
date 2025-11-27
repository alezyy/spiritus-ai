import os
import sys

def patch_file(file_path, search_text, replace_text, check_text=None):
    """
    Patches a file by replacing search_text with replace_text.
    If check_text is provided, it checks if check_text is already in the file to avoid re-patching.
    If check_text is NOT provided, it checks if replace_text is already in the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return False

    if check_text:
        if check_text in content:
            print(f"Already patched: {file_path}")
            return True
    else:
        if replace_text in content:
            print(f"Already patched: {file_path}")
            return True

    if search_text not in content:
        print(f"Warning: Search text not found in {file_path}. Skipping.")
        return False

    new_content = content.replace(search_text, replace_text)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully patched: {file_path}")
    return True

def append_to_file(file_path, text_to_append, check_text=None):
    """
    Appends text to the end of a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return False

    check = check_text if check_text else text_to_append.strip()
    if check in content:
        print(f"Already patched: {file_path}")
        return True

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + text_to_append + "\n")
    
    print(f"Successfully patched: {file_path}")
    return True

def main():
    print("Starting Open WebUI Subscription Integration Installation...")
    
    # 1. Patch requirements.txt
    append_to_file("backend/requirements.txt", "stripe", check_text="stripe")

    # 2. Patch backend/open_webui/main.py
    # Add router
    patch_file(
        "backend/open_webui/main.py",
        "    scim,\n    payments,\n)",
        "    scim,\n    payments,\n)", # Already there in search_text if user ran it, but let's be safe
        check_text="payments,"
    )
    # If not found (fresh install), try to find the line before
    patch_file(
        "backend/open_webui/main.py",
        "    scim,\n)",
        "    scim,\n    payments,\n)",
        check_text="payments,"
    )

    # 3. Patch backend/open_webui/models/users.py
    # We need to insert the method into the class. This is tricky with simple replace.
    # We'll look for a known method and insert before it.
    user_method_code = """
    def get_user_by_stripe_customer_id(self, customer_id: str) -> Optional[UserModel]:
        try:
            with get_db() as db:
                # This is a bit inefficient as we are scanning all users, but since info is a JSON field
                # and we don't have a generated column or index on it, this is the way for now.
                # For production with many users, we should add a dedicated column or index.
                users = db.query(User).all()
                for user in users:
                    if user.info and user.info.get("stripe_customer_id") == customer_id:
                        return UserModel.model_validate(user)
                return None
        except Exception:
            return None
"""
    patch_file(
        "backend/open_webui/models/users.py",
        "    def get_users(",
        user_method_code + "\n    def get_users(",
        check_text="get_user_by_stripe_customer_id"
    )

    # 4. Patch src/lib/components/layout/Sidebar/UserMenu.svelte
    # Add menu item
    menu_item_code = """
			<DropdownMenu.Item
				class="flex gap-2 items-center px-3 py-2 text-sm  font-medium cursor-pointer"
				on:click={() => {
					goto('/subscription');
				}}
			>
				<Sparkles className="size-4" />
				<div class="flex items-center">Subscription</div>
			</DropdownMenu.Item>
"""
    patch_file(
        "src/lib/components/layout/Sidebar/UserMenu.svelte",
        '<DropdownMenu.Item',
        menu_item_code + '\n			<DropdownMenu.Item',
        check_text="Subscription"
    )
    
    # Add import for Sparkles if missing
    patch_file(
        "src/lib/components/layout/Sidebar/UserMenu.svelte",
        "import {",
        "import { Sparkles, ",
        check_text="Sparkles"
    )

    # 5. Patch docker-compose.yaml
    patch_file(
        "docker-compose.yaml",
        "    container_name: open-webui",
        "    container_name: open-webui\n    env_file:\n      - .env",
        check_text="env_file:"
    )
    
    patch_file(
        "docker-compose.yaml",
        "    image: ghcr.io/open-webui/open-webui:main",
        "    build:\n      context: .\n      dockerfile: Dockerfile\n    image: open-webui:custom",
        check_text="build:"
    )
    # Handle the versioned image tag case too
    patch_file(
        "docker-compose.yaml",
        "    image: ghcr.io/open-webui/open-webui:0.6.36",
        "    build:\n      context: .\n      dockerfile: Dockerfile\n    image: open-webui:custom",
        check_text="build:"
    )

    print("\nInstallation script completed.")
    print("Please ensure you have created the .env file with your Stripe keys.")
    print("Then run: docker-compose up -d --build")

if __name__ == "__main__":
    main()
