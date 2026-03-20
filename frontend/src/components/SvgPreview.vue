<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    svg: string
    kind: 'symbol' | 'footprint'
    initialScale?: number
    gridSquareMm?: number
  }>(),
  {
    initialScale: 1,
    gridSquareMm: 1,
  },
)

const scale = ref(props.initialScale)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)

let lastPointerX = 0
let lastPointerY = 0

const minScale = computed(() => (props.kind === 'symbol' ? 1 : 0.75))
const maxScale = 4

const scaleLabel = computed(() => `${Math.round(scale.value * 100)}%`)
const footprintScaleLabel = computed(
  () => `Zoom ${scaleLabel.value} · Grid 1 square = ${props.gridSquareMm.toFixed(2)} mm`,
)
const contentStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${scale.value})`,
}))

const clampScale = (value: number) => Math.min(maxScale, Math.max(minScale.value, value))

const resetView = () => {
  scale.value = props.initialScale
  panX.value = 0
  panY.value = 0
}

const zoomBy = (delta: number) => {
  scale.value = clampScale(Number((scale.value + delta).toFixed(2)))
}

const onWheel = (event: WheelEvent) => {
  event.preventDefault()
  zoomBy(event.deltaY < 0 ? 0.16 : -0.16)
}

const onPointerDown = (event: PointerEvent) => {
  if (event.button !== 0) {
    return
  }
  isDragging.value = true
  lastPointerX = event.clientX
  lastPointerY = event.clientY
  ;(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId)
}

const onPointerMove = (event: PointerEvent) => {
  if (!isDragging.value) {
    return
  }
  panX.value += event.clientX - lastPointerX
  panY.value += event.clientY - lastPointerY
  lastPointerX = event.clientX
  lastPointerY = event.clientY
}

const stopDragging = (event?: PointerEvent) => {
  if (event) {
    ;(event.currentTarget as HTMLElement).releasePointerCapture(event.pointerId)
  }
  isDragging.value = false
}

watch(
  () => props.svg,
  () => resetView(),
  { immediate: true },
)
</script>

<template>
  <div
    class="svg-panel svg-panel--interactive"
    :class="{ 'is-dragging': isDragging }"
    @wheel="onWheel"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="stopDragging"
    @pointercancel="stopDragging"
    @pointerleave="stopDragging"
    @dblclick="resetView"
  >
    <div class="svg-panel__toolbar">
      <button type="button" class="svg-panel__tool" aria-label="Zoom out" @click.stop="zoomBy(-0.16)">
        -
      </button>
      <button type="button" class="svg-panel__tool svg-panel__tool--label" @click.stop="resetView">
        {{ scaleLabel }}
      </button>
      <button type="button" class="svg-panel__tool" aria-label="Zoom in" @click.stop="zoomBy(0.16)">
        +
      </button>
    </div>

    <div class="svg-panel__viewport">
      <div class="svg-panel__content" :style="contentStyle" v-html="svg" />
    </div>

    <div v-if="kind === 'footprint'" class="svg-panel__scale">
      {{ footprintScaleLabel }}
    </div>
  </div>
</template>
