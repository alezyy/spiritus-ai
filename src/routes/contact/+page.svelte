<script>
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

		<div class="bg-gray-50 dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700 shadow-sm">
			<div class="flex items-center gap-3 mb-6">
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

				<div class="grid gap-4">
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
</div>
