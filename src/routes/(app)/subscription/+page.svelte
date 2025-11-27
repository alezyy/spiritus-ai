<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { user } from '$lib/stores';
	import {
		createCheckoutSession,
		createPortalSession,
		getSubscriptionStatus
	} from '$lib/apis/payments';
	import { toast } from 'svelte-sonner';
	import Spinner from '$lib/components/common/Spinner.svelte';

	let loading = true;
	let subscription: any = null;
	const i18n = getContext('i18n');

	onMount(async () => {
		if (!$user) {
			await goto('/auth');
			return;
		}

		const success = $page.url.searchParams.get('success');
		const canceled = $page.url.searchParams.get('canceled');

		if (success) {
			toast.success($i18n.t('Subscription successful! Thank you for upgrading.'));
		} else if (canceled) {
			toast.error($i18n.t('Subscription canceled.'));
		}

		await loadSubscription();
	});

	const loadSubscription = async () => {
		loading = true;
		try {
			subscription = await getSubscriptionStatus(localStorage.token);
		} catch (error) {
			console.error(error);
			toast.error($i18n.t('Failed to load subscription status'));
		} finally {
			loading = false;
		}
	};

	const handleUpgrade = async () => {
		try {
			const res = await createCheckoutSession(localStorage.token);
			if (res && res.url) {
				window.location.href = res.url;
			}
		} catch (error) {
			console.error(error);
			toast.error('Failed to start checkout session');
		}
	};

	const handleManage = async () => {
		try {
			const res = await createPortalSession(localStorage.token);
			if (res && res.url) {
				window.location.href = res.url;
			}
		} catch (error) {
			console.error(error);
			toast.error('Failed to open billing portal');
		}
	};
</script>

<div class="min-h-screen w-full flex justify-center items-center font-primary">
	<div
		class="w-full max-w-lg p-8 bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800"
	>
		<div class="text-center mb-8">
			<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
				{$i18n.t('Subscription')}
			</h1>
			<p class="text-gray-600 dark:text-gray-400">
				{$i18n.t('Manage your Open WebUI subscription')}
			</p>
		</div>

		{#if loading}
			<div class="flex justify-center py-12">
				<Spinner className="size-8" />
			</div>
		{:else if subscription}
			{@const isActive = ['active', 'trialing'].includes(subscription.status)}
			<div class="space-y-6">
				<div
					class="p-6 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700"
				>
					<div class="flex justify-between items-center mb-4">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400"
							>{$i18n.t('Current Plan')}</span
						>
						<span
							class="px-3 py-1 text-sm font-semibold rounded-full
							{isActive
								? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
								: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'}"
						>
							{isActive
								? subscription.status === 'trialing'
									? $i18n.t('Plus (Trial)')
									: $i18n.t('Plus')
								: $i18n.t('Free')}
						</span>
					</div>

					{#if isActive}
						{#if subscription.current_period_end && subscription.current_period_end > 1600000000}
							<div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
								{$i18n.t('Your subscription renews on')}
								{new Date(subscription.current_period_end * 1000).toLocaleDateString()}.
							</div>
						{/if}
						<button
							class="w-full py-3 px-4 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium rounded-lg border border-gray-200 dark:border-gray-600 transition-colors"
							on:click={handleManage}
						>
							{$i18n.t('Manage Subscription')}
						</button>
					{:else}
						<div class="mb-6">
							<div class="text-2xl font-bold text-gray-900 dark:text-white mb-1">
								$20<span class="text-base font-normal text-gray-500">/{$i18n.t('month')}</span>
							</div>
							<ul class="space-y-3 mt-4 text-gray-600 dark:text-gray-300">
								<li class="flex items-center gap-2">
									<svg
										class="w-5 h-5 text-green-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										><path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 13l4 4L19 7"
										></path></svg
									>
									{$i18n.t('Access to advanced models')}
								</li>
								<li class="flex items-center gap-2">
									<svg
										class="w-5 h-5 text-green-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										><path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 13l4 4L19 7"
										></path></svg
									>
									{$i18n.t('Faster response times')}
								</li>
								<li class="flex items-center gap-2">
									<svg
										class="w-5 h-5 text-green-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
										><path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M5 13l4 4L19 7"
										></path></svg
									>
									{$i18n.t('Priority support')}
								</li>
							</ul>
						</div>
						<button
							class="w-full py-3 px-4 bg-black dark:bg-white hover:bg-gray-800 dark:hover:bg-gray-100 text-white dark:text-black font-bold rounded-lg transition-colors"
							on:click={handleUpgrade}
						>
							{$i18n.t('Upgrade to Plus')}
						</button>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
