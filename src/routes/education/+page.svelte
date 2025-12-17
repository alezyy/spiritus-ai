<script>
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';
	import Play from '$lib/components/icons/Play.svelte';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>{$i18n.t('Video formation')} | {$WEBUI_NAME}</title>
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
</div>
