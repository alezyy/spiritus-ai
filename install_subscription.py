import os
import json

def patch_file(file_path, search_text, replace_text, check_text=None):
    """
    Patches a file by replacing search_text with replace_text.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return False

    if check_text and check_text in content:
        print(f"Already patched (check_text found): {file_path}")
        return True
    
    # If check_text is NOT provided, check if replace_text is already there (simple check)
    if not check_text and replace_text in content:
        print(f"Already patched (replace_text found): {file_path}")
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

def update_json_file(file_path, new_entries):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        for key, value in new_entries.items():
            if key not in data:
                data[key] = value
                updated = True
            # Optional: Update value if it's different? For now, we only add if missing to avoid overwriting user changes
            # But the user asked for updates, so maybe we should ensure values match?
            # Let's enforce values for the specific keys we know about.
            elif data[key] != value:
                 data[key] = value
                 updated = True

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully updated translation: {file_path}")
        else:
            print(f"No changes needed for: {file_path}")

    except Exception as e:
        print(f"Error updating JSON {file_path}: {e}")

def create_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created/Updated file: {file_path}")

def main():
    print("Starting Open WebUI Subscription & Customization Installation...")
    
    # ==============================================================================
    # 1. Backend & Subscription Patches
    # ==============================================================================

    # Patch requirements.txt
    append_to_file("backend/requirements.txt", "stripe", check_text="stripe")

    # Patch backend/open_webui/main.py (Router)
    patch_file(
        "backend/open_webui/main.py",
        "    scim,\n    payments,\n)",
        "    scim,\n    payments,\n)", 
        check_text="payments,"
    )
    patch_file(
        "backend/open_webui/main.py",
        "    scim,\n)",
        "    scim,\n    payments,\n)",
        check_text="payments,"
    )

    # Patch backend/open_webui/models/users.py (Stripe Method)
    user_method_code = """
    def get_user_by_stripe_customer_id(self, customer_id: str) -> Optional[UserModel]:
        try:
            with get_db() as db:
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

    # Patch backend/open_webui/env.py (Remove postfix)
    patch_file(
        "backend/open_webui/env.py",
        'if WEBUI_NAME != "Open WebUI":',
        '# if WEBUI_NAME != "Open WebUI":',
        check_text='# if WEBUI_NAME != "Open WebUI":'
    )
    patch_file(
        "backend/open_webui/env.py",
        '    WEBUI_NAME += " (Open WebUI)"',
        '#     WEBUI_NAME += " (Open WebUI)"',
        check_text='#     WEBUI_NAME += " (Open WebUI)"'
    )

    # Patch docker-compose.yaml
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
    # Handle versioned image tag
    with open("docker-compose.yaml", "r") as f:
        dc_content = f.read()
    if "image: ghcr.io/open-webui/open-webui:" in dc_content and "build:" not in dc_content:
         # Generic patch for any version tag if build is missing
         import re
         new_dc = re.sub(r"image: ghcr.io/open-webui/open-webui:.*", "build:\n      context: .\n      dockerfile: Dockerfile\n    image: open-webui:custom", dc_content)
         with open("docker-compose.yaml", "w") as f:
             f.write(new_dc)
         print("Patched docker-compose.yaml (Regex)")

    # ==============================================================================
    # 2. UI Customization (UserMenu.svelte)
    # ==============================================================================
    
    # 2.1 Add Subscription Item
    menu_item_code = """
				<DropdownMenu.Item
					class="flex gap-2 items-center px-3 py-2 text-sm  font-medium cursor-pointer"
					on:click={() => {
						goto('/subscription');
					}}
				>
					<Sparkles className="size-4" />
					<div class="flex items-center">{$i18n.t('Subscription')}</div>
				</DropdownMenu.Item>
"""
    # Check if Subscription is already added
    patch_file(
        "src/lib/components/layout/Sidebar/UserMenu.svelte",
        '<DropdownMenu.Item',
        menu_item_code + '\n				<DropdownMenu.Item', # Indentation matters
        check_text="Subscription'" # Check for the i18n key or text
    )

    # 2.2 Add Imports
    imports_to_add = [
        "import Sparkles from '$lib/components/icons/Sparkles.svelte';",
        "import Envelope from '$lib/components/icons/Envelope.svelte';",
        "import Play from '$lib/components/icons/Play.svelte';",
        "import ChevronRight from '$lib/components/icons/ChevronRight.svelte';",
        "import QuestionMarkCircle from '$lib/components/icons/QuestionMarkCircle.svelte';",
        "import PencilSquare from '$lib/components/icons/PencilSquare.svelte';",
        "import DocumentText from '$lib/components/icons/DocumentText.svelte';",
        "import Flag from '$lib/components/icons/Flag.svelte';",
        "import Bolt from '$lib/components/icons/Bolt.svelte';",
        "import SignOut from '$lib/components/icons/SignOut.svelte';"
    ]
    
    user_menu_path = "src/lib/components/layout/Sidebar/UserMenu.svelte"
    with open(user_menu_path, 'r') as f:
        um_content = f.read()
    
    imports_block = ""
    for imp in imports_to_add:
        # Check if import exists (sloppy check, but works for unique names)
        name = imp.split("import ")[1].split(" from")[0].strip().replace("{", "").replace("}", "").replace(",", "")
        if name not in um_content:
            imports_block += imp + "\n\t"
            
    if imports_block:
         patch_file(
            user_menu_path,
            "import { showSettings",
            imports_block + "import { showSettings",
            check_text=None
         )

    # 2.3 Replace Help Menu with Submenu
    # We look for the standard Help Item and replace it if found.
    # If the user has already modified it, we might skip or force update.
    # We will assume if "QuestionMarkCircle" and "Help" are present but NO "DropdownMenu.Sub", we need to patch.
    
    help_submenu_code = """
				<DropdownMenu.Sub>
					<DropdownMenu.SubTrigger
						class="flex justify-between rounded-xl py-1.5 px-3 w-full hover:bg-gray-50 dark:hover:bg-gray-800 transition cursor-pointer"
					>
						<div class="flex items-center">
							<div class="self-center mr-3">
								<QuestionMarkCircle className="size-5" strokeWidth="1.5" />
							</div>
							<div class="self-center truncate">{$i18n.t('Help')}</div>
						</div>
						<div class="self-center">
							<ChevronRight className="size-4" />
						</div>
					</DropdownMenu.SubTrigger>
					<DropdownMenu.SubContent
						class="w-full max-w-[200px] rounded-2xl px-1 py-1 border border-gray-100 dark:border-gray-800 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg text-sm"
						sideOffset={8}
						side="right"
						align="start"
					>
						<DropdownMenu.Item
							as="a"
							href="/contact"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
						>
							<Envelope className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Contact')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							as="a"
							href="/education"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
						>
							<Play className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Video Training')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							as="a"
							href="https://docs.openwebui.com"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
						>
							<QuestionMarkCircle className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Help center')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							as="a"
							href="https://github.com/open-webui/open-webui/releases"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
						>
							<PencilSquare className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Release notes')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							as="a"
							href="/terms"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
						>
							<DocumentText className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Terms & Policies')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							as="a"
							href="https://github.com/open-webui/open-webui/issues/new/choose"
							target="_blank"
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer my-1"
						>
							<Flag className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Report Bug')}</div>
						</DropdownMenu.Item>

						<DropdownMenu.Item
							class="flex gap-3 items-center py-2 px-3 text-sm select-none w-full hover:bg-gray-50 dark:hover:bg-gray-800 rounded-xl transition cursor-pointer"
							on:click={async () => {
								show = false;
								showShortcuts.set(!$showShortcuts);

								if ($mobile) {
									await tick();
									showSidebar.set(false);
								}
							}}
						>
							<Bolt className="size-5" strokeWidth="1.5" />
							<div class="flex items-center">{$i18n.t('Keyboard shortcuts')}</div>
						</DropdownMenu.Item>
					</DropdownMenu.SubContent>
				</DropdownMenu.Sub>
"""
    # This matching is brittle, but sufficient for the specified request context.
    # We look for the standard Help item.
    original_help_item = """				<DropdownMenu.Item
					class="flex rounded-xl py-1.5 px-3 w-full hover:bg-gray-50 dark:hover:bg-gray-800 transition cursor-pointer"
					on:click={async () => {
						show = false;
						showShortcuts.set(!$showShortcuts);

						if ($mobile) {
							await tick();
							showSidebar.set(false);
						}
					}}
				>
					<div class=" self-center mr-3">
						<QuestionMarkCircle className="size-5" strokeWidth="1.5" />
					</div>
					<div class=" self-center truncate">{$i18n.t('Help')}</div>
				</DropdownMenu.Item>"""

    # Note: Structure varies. Let's not try to replace the big block if we can't find it exactly.
    # Instead, we will assume that if we don't find "DropdownMenu.Sub", we append it? No, needs position.
    
    # Strategy: Read file, if "DropdownMenu.Sub" not found, try to find "Archived Chats" item and insert AFTER it.
    if '<DropdownMenu.Sub>' not in um_content:
         print("Patching UserMenu to include Help Submenu...")
         # Find insertion point: After Admin Panel item or Archived Chats
         # We'll use start of "Sign Out" separator as a safe anchor for "Before"
         anchor = '<hr class=" border-gray-50 dark:border-gray-800 my-1 p-0" />'
         if anchor in um_content:
             patch_file(user_menu_path, anchor, help_submenu_code + "\n\n" + anchor, check_text="<DropdownMenu.Sub>")
    else:
         print("UserMenu already contains Submenu (or Sub found). Skipping complex patch.")

    # ==============================================================================
    # 3. Create Custom Pages
    # ==============================================================================
    
    # 3.1 Contact Page
    contact_page = """<script>
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';
	import Envelope from '$lib/components/icons/Envelope.svelte';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>{$i18n.t('Contact Us')} | {$WEBUI_NAME}</title>
</svelte:head>

<div class="h-screen w-full flex justify-center p-6 bg-white dark:bg-gray-900 dark:text-gray-100 overflow-y-auto">
	<div class="max-w-2xl w-full">
		<div class="mb-8">
			<a href="/" class="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-300 transition flex items-center gap-1">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
					<path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd" />
				</svg>
				{$i18n.t('Back to Home')}
			</a>
		</div>

		<div class="flex flex-col gap-8">
			<div class="flex items-center gap-3">
				<div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full text-blue-600 dark:text-blue-400">
					<Envelope className="size-6" strokeWidth="1.5" />
				</div>
				<h1 class="text-3xl font-bold">{$i18n.t('Contact Us')}</h1>
			</div>

			<div class="space-y-6">
				<div>
					<h2 class="text-xl font-semibold mb-2">{$i18n.t('Customer Services')}</h2>
					<p class="text-gray-600 dark:text-gray-400">
						{$i18n.t('For any questions or assistance, our team is at your disposal.')}
					</p>
				</div>

				<div class="flex flex-col gap-4 p-6 bg-gray-50 dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
					<div class="flex flex-col">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{$i18n.t('Email')}</span>
						<a href="mailto:info@missionaec.com" class="text-lg font-medium text-blue-600 dark:text-blue-400 hover:underline">
							info@missionaec.com
						</a>
					</div>

					<div class="flex flex-col">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{$i18n.t('Phone')}</span>
						<a href="tel:+14387657686" class="text-lg font-medium hover:text-blue-600 dark:hover:text-blue-400 transition">
							438-765-7686
						</a>
					</div>

					<div class="flex flex-col">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{$i18n.t('Address')}</span>
						<span class="text-lg">
							MAEC Montréal, QC
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>"""
    create_file("src/routes/contact/+page.svelte", contact_page)

    # 3.2 Education Page
    education_page = """<script>
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';
	import Play from '$lib/components/icons/Play.svelte';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>{$i18n.t('Video Training')} | {$WEBUI_NAME}</title>
</svelte:head>

<div class="h-screen w-full flex justify-center p-6 bg-white dark:bg-gray-900 dark:text-gray-100 overflow-y-auto">
	<div class="max-w-4xl w-full">
		<div class="mb-8">
			<a href="/" class="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-300 transition flex items-center gap-1">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
					<path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd" />
				</svg>
				{$i18n.t('Back to Home')}
			</a>
		</div>

		<div class="flex items-center gap-3 mb-6">
			<div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full text-blue-600 dark:text-blue-400">
				<Play className="size-6" strokeWidth="1.5" />
			</div>
			<h1 class="text-3xl font-bold">{$i18n.t('Video Training')}</h1>
		</div>

		<div class="prose dark:prose-invert max-w-none">
			<p class="text-lg mb-8">
				{$i18n.t('To learn how to use Spiritus AI, follow these instructions:')}
			</p>
			
			<div class="flex flex-col gap-6">
				<div class="w-full aspect-video rounded-xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">
					<iframe
						class="w-full h-full"
						src="https://www.youtube.com/embed/F9Qr0oqncDc"
						title="Formation Spiritus AI"
						frameborder="0"
						allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
						referrerpolicy="strict-origin-when-cross-origin"
						allowfullscreen
					></iframe>
				</div>
				<p class="text-sm text-gray-500 text-center">
					{$i18n.t('Watch the video above to learn the basics.')}
				</p>
			</div>
		</div>
	</div>
</div>"""
    create_file("src/routes/education/+page.svelte", education_page)

    # 3.3 Terms Page
    terms_page = """<script>
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>{$i18n.t('Terms & Policies')} | {$WEBUI_NAME}</title>
</svelte:head>

<div class="h-screen w-full flex justify-center p-6 bg-white dark:bg-gray-900 dark:text-gray-100 overflow-y-auto">
	<div class="max-w-4xl w-full">
		<div class="mb-8">
			<a href="/" class="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-300 transition flex items-center gap-1">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
					<path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd" />
				</svg>
				{$i18n.t('Back to Home')}
			</a>
		</div>

		<h1 class="text-3xl font-bold mb-2">{$i18n.t('Terms & Policies (Law 25)')}</h1>
		<p class="text-sm text-gray-500 mb-8">{$i18n.t('Last updated:')} {new Date().toLocaleDateString()}</p>

		<div class="prose dark:prose-invert max-w-none text-gray-800 dark:text-gray-200">
			
			<div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mb-8">
				<h3 class="text-lg font-bold mb-2">{$i18n.t('Data Protection Officer')}</h3>
				<p class="text-sm">
					{$i18n.t('In accordance with Law 25, here are the contact details of the person responsible for data protection for {{WEBUI_NAME}}:', { WEBUI_NAME: $WEBUI_NAME })}
				</p>
				<ul class="text-sm list-none pl-0 mt-2 space-y-1">
					<li><strong>{$i18n.t('Name:')}</strong> Francener Alézy</li>
					<li><strong>{$i18n.t('Title:')}</strong> {$i18n.t('Data Protection Officer')}</li>
					<li><strong>{$i18n.t('Email:')}</strong> <a href="mailto:info@missionaec.com" class="text-blue-600 dark:text-blue-400">info@missionaec.com</a></li>
					<li><strong>{$i18n.t('Address:')}</strong> Montréal</li>
				</ul>
			</div>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('1. Introduction and Acceptance')}</h2>
				<p class="mb-4">
					{$i18n.t('Welcome to {{WEBUI_NAME}}. By using our platform, you agree to these terms and our privacy policy. We are committed to protecting your personal information in accordance with applicable laws in Quebec, particularly the Act respecting the protection of personal information in the private sector (as amended by Law 25).', { WEBUI_NAME: $WEBUI_NAME })}
				</p>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('2. Collection of Personal Information')}</h2>
				<p class="mb-2">{$i18n.t('We collect only the information necessary for the proper functioning of our services:')}</p>
				<ul class="list-disc pl-6 space-y-2 mb-4">
					<li><strong>{$i18n.t('Identification Information:')}</strong> {$i18n.t('Name, first name, email address (for account creation and authentication).')}</li>
					<li><strong>{$i18n.t('Usage Data:')}</strong> {$i18n.t('Conversation history, user preferences, and connection logs for security.')}</li>
					<li><strong>{$i18n.t('Payment Information:')}</strong> {$i18n.t('Processed securely by our partner Stripe (we do not store your full credit card numbers).')}</li>
				</ul>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('3. Use and Communication of Data')}</h2>
				<p class="mb-4">
					{$i18n.t('Your data is used to:')}
				</p>
				<ul class="list-disc pl-6 space-y-2 mb-4">
					<li>{$i18n.t('Provide, maintain, and improve our AI services.')}</li>
					<li>{$i18n.t('Manage your subscription and payments.')}</li>
					<li>{$i18n.t('Communicate with you regarding updates or technical issues.')}</li>
				</ul>
				<p class="mb-4">
					{$i18n.t('We never sell your personal data. It may be shared with third-party service providers (hosting, payment processing) only as necessary to fulfill their mandates and under strict confidentiality agreements.')}
				</p>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('4. Retention and Security')}</h2>
				<p class="mb-4">
					{$i18n.t('Your personal information is stored on secure servers. We implement reasonable physical, organizational, and technological security measures to protect your information against unauthorized access, disclosure, or loss.')}
				</p>
				<p class="mb-4">
					<strong>{$i18n.t('Storage Location:')}</strong> {$i18n.t('Your data is primarily hosted in Quebec/Canada. If data is transferred outside Quebec, we ensure it receives adequate protection.')}
				</p>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('5. Your Rights (Law 25)')}</h2>
				<p class="mb-4">{$i18n.t('In accordance with Law 25, you have the following rights:')}</p>
				<ul class="list-disc pl-6 space-y-2 mb-4">
					<li><strong>{$i18n.t('Right of access:')}</strong> {$i18n.t('You can request to access the personal information we hold about you.')}</li>
					<li><strong>{$i18n.t('Right to rectification:')}</strong> {$i18n.t('You can request the correction of inaccurate or incomplete information.')}</li>
					<li><strong>{$i18n.t('Right to erasure:')}</strong> {$i18n.t('You can request the deletion of your account and data, subject to legal retention obligations.')}</li>
					<li><strong>{$i18n.t('Right to portability:')}</strong> {$i18n.t('You can request to obtain your data in a structured and commonly used technological format.')}</li>
					<li><strong>{$i18n.t('Withdrawal of consent:')}</strong> {$i18n.t('You can withdraw your consent to the use of your data at any time (which may limit access to our services).')}</li>
				</ul>
				<p class="mt-4">
					{$i18n.t('To exercise these rights, please contact our Data Protection Officer indicated at the top of this page.')}
				</p>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('6. Terms of Use')}</h2>
				<p class="mb-4">
					{$i18n.t('By using {{WEBUI_NAME}}, you agree not to use the service for illegal, defamatory, or harmful purposes. We reserve the right to suspend or terminate any account that does not respect these conditions.', { WEBUI_NAME: $WEBUI_NAME })}
				</p>
			</section>

			<section class="mb-10">
				<h2 class="text-2xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">{$i18n.t('7. Privacy Incidents')}</h2>
				<p class="mb-4">
					{$i18n.t('We maintain a register of privacy incidents. In the event of an incident presenting a risk of serious injury, we will notify the Commission d\'accès à l\'information du Québec and the individuals concerned as soon as possible.')}
				</p>
			</section>

		</div>
	</div>
</div>"""
    create_file("src/routes/terms/+page.svelte", terms_page)

    # ==============================================================================
    # 4. Translations
    # ==============================================================================
    
    fr_updates = {
	"Upgrade to Plus": "Passer à Plus",
	"Back to Home": "Retour à l'accueil",
	"Video Training": "Formation Vidéo",
	"To learn how to use Spiritus AI, follow these instructions:": "Pour savoir comment utiliser Spiritus AI, suivez les instructions suivantes :",
	"Watch the video above to learn the basics.": "Regardez la vidéo ci-dessus pour apprendre les bases.",
	"Contact Us": "Nous Contacter",
	"Customer Services": "Services clients",
	"For any questions or assistance, our team is at your disposal.": "Pour toute question ou assistance, notre équipe est à votre disposition.",
	"Email": "Courriel",
	"Phone": "Téléphone",
	"Address": "Adresse",
	"Terms & Policies": "Termes et Politiques",
	"Terms & Policies (Law 25)": "Termes et Politiques (Loi 25)",
	"Last updated:": "Dernière mise à jour :",
	"Data Protection Officer": "Responsable de la protection des renseignements personnels",
	"In accordance with Law 25, here are the contact details of the person responsible for data protection for {{WEBUI_NAME}}:": "Conformément à la Loi 25, voici les coordonnées de la personne responsable de la protection des données pour {{WEBUI_NAME}} :",
	"Name:": "Nom :",
	"Title:": "Titre :",
	"Email:": "Courriel :",
	"Address:": "Adresse :",
	"1. Introduction and Acceptance": "1. Introduction et Acceptation",
	"Welcome to {{WEBUI_NAME}}. By using our platform, you agree to these terms and our privacy policy. We are committed to protecting your personal information in accordance with applicable laws in Quebec, particularly the Act respecting the protection of personal information in the private sector (as amended by Law 25).": "Bienvenue sur {{WEBUI_NAME}}. En utilisant notre plateforme, vous acceptez les présentes conditions ainsi que notre politique de confidentialité. Nous nous engageons à protéger vos renseignements personnels conformément aux lois en vigueur au Québec, notamment la Loi sur la protection des renseignements personnels dans le secteur privé (telle que modifiée par la Loi 25).",
	"2. Collection of Personal Information": "2. Collecte des Renseignements Personnels",
	"We collect only the information necessary for the proper functioning of our services:": "Nous collectons uniquement les renseignements nécessaires au bon fonctionnement de nos services :",
	"Identification Information:": "Informations d'identification :",
	"Name, first name, email address (for account creation and authentication).": "Nom, prénom, adresse courriel (pour la création de compte et l'authentification).",
	"Usage Data:": "Données d'utilisation :",
	"Conversation history, user preferences, and connection logs for security.": "Historique des conversations, préférences de l'utilisateur et journaux de connexion (logs) pour assurer la sécurité.",
	"Payment Information:": "Informations de paiement :",
	"Processed securely by our partner Stripe (we do not store your full credit card numbers).": "Traitées de manière sécurisée par notre partenaire Stripe (nous ne conservons pas vos numéros de carte de crédit complets).",
	"3. Use and Communication of Data": "3. Utilisation et Communication des Données",
	"Your data is used to:": "Vos données sont utilisées pour :",
	"Provide, maintain, and improve our AI services.": "Fournir, maintenir et améliorer nos services d'intelligence artificielle.",
	"Manage your subscription and payments.": "Gérer votre abonnement et vos paiements.",
	"Communicate with you regarding updates or technical issues.": "Communiquer avec vous concernant des mises à jour ou des problèmes techniques.",
	"We never sell your personal data. It may be shared with third-party service providers (hosting, payment processing) only as necessary to fulfill their mandates and under strict confidentiality agreements.": "Nous ne vendons jamais vos données personnelles. Elles peuvent être communiquées à des tiers fournisseurs de services (hébergement, traitement de paiement) uniquement dans la mesure nécessaire à l'exécution de leurs mandats et sous des ententes de confidentialité strictes.",
	"4. Retention and Security": "4. Conservation et Sécurité",
	"Your personal information is stored on secure servers. We implement reasonable physical, organizational, and technological security measures to protect your information against unauthorized access, disclosure, or loss.": "Vos renseignements personnels sont conservés sur des serveurs sécurisés. Nous mettons en œuvre des mesures de sécurité physiques, organisationnelles et technologiques raisonnables pour protéger vos informations contre l'accès non autorisé, la divulgation ou la perte.",
	"Storage Location:": "Lieu de conservation :",
	"Your data is primarily hosted in Quebec/Canada. If data is transferred outside Quebec, we ensure it receives adequate protection.": "Vos données sont principalement hébergées au Québec/Canada. Si des données sont transférées hors du Québec, nous nous assurons qu'elles bénéficient d'une protection adéquate.",
	"5. Your Rights (Law 25)": "5. Vos Droits (Loi 25)",
	"In accordance with Law 25, you have the following rights:": "Conformément à la Loi 25, vous disposez des droits suivants :",
	"Right of access:": "Droit d'accès :",
	"You can request to access the personal information we hold about you.": "Vous pouvez demander à consulter les renseignements personnels que nous détenons à votre sujet.",
	"Right to rectification:": "Droit de rectification :",
	"You can request the correction of inaccurate or incomplete information.": "Vous pouvez demander la correction de renseignements inexacts ou incomplets.",
	"Right to erasure:": "Droit à l'effacement :",
	"You can request the deletion of your account and data, subject to legal retention obligations.": "Vous pouvez demander la suppression de votre compte et de vos données, sous réserve des obligations légales de conservation.",
	"Right to portability:": "Droit à la portabilité :",
	"You can request to obtain your data in a structured and commonly used technological format.": "Vous pouvez demander d'obtenir vos données dans un format technologique structuré et couramment utilisé.",
	"Withdrawal of consent:": "Retrait du consentement :",
	"You can withdraw your consent to the use of your data at any time (which may limit access to our services).": "Vous pouvez retirer votre consentement à l'utilisation de vos données à tout moment (ce qui pourrait limiter l'accès à nos services).",
	"To exercise these rights, please contact our Data Protection Officer indicated at the top of this page.": "Pour exercer ces droits, veuillez contacter notre Responsable de la protection des renseignements personnels indiqué en haut de cette page.",
	"6. Terms of Use": "6. Conditions d'Utilisation",
	"By using {{WEBUI_NAME}}, you agree not to use the service for illegal, defamatory, or harmful purposes. We reserve the right to suspend or terminate any account that does not respect these conditions.": "En utilisant {{WEBUI_NAME}}, vous acceptez de ne pas utiliser le service à des fins illégales, diffamatoires ou nuisibles. Nous nous réservons le droit de suspendre ou de résilier tout compte ne respectant pas ces conditions.",
	"7. Privacy Incidents": "7. Incidents de Confidentialité",
	"We maintain a register of privacy incidents. In the event of an incident presenting a risk of serious injury, we will notify the Commission d'accès à l'information du Québec and the individuals concerned as soon as possible.": "Nous tenons un registre des incidents de confidentialité. En cas d'incident présentant un risque de préjudice sérieux, nous aviserons la Commission d'accès à l'information du Québec ainsi que les personnes concernées dans les meilleurs délais."
    }

    # For English, we use empty strings for keys (which usually fallbacks or just acts as keys)
    # The user manual modification used empty strings for values.
    en_updates = {key: "" for key in fr_updates.keys()}
    en_updates["Upgrade to Plus"] = "Upgrade to Plus" # Exception if needed, but existing en-US file has specific values.
    # Actually, let's keep English keys as English text if possible, or just empty if that's the convention in this file.
    # Looking at the file, most values are empty strings which implies the key IS the english text.
    # So { "Upgrade to Plus": "" } is correct.

    update_json_file("src/lib/i18n/locales/fr-CA/translation.json", fr_updates)
    update_json_file("src/lib/i18n/locales/en-US/translation.json", en_updates)


    print("\nInstallation script completed.")
    print("Please ensure you have created the .env file with your Stripe keys.")
    print("Then run: docker-compose up -d --build")

if __name__ == "__main__":
    main()
