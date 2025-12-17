<script>
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
</div>
