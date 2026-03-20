<script setup lang="ts">
defineProps<{
  title: string
  subtitle: string
}>()
</script>

<template>
  <section class="preview-card">
    <header class="preview-card__header">
      <div>
        <h3>{{ title }}</h3>
        <p>{{ subtitle }}</p>
      </div>
      <slot name="header-extra" />
    </header>
    <div class="preview-card__body">
      <slot />
    </div>
  </section>
</template>
