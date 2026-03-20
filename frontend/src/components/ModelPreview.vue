<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AmbientLight,
  Box3,
  Color,
  DirectionalLight,
  Object3D,
  PerspectiveCamera,
  Scene,
  Vector3,
  WebGLRenderer,
} from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { VRMLLoader } from 'three/examples/jsm/loaders/VRMLLoader.js'

const props = defineProps<{
  available: boolean
  wrlUrl: string | null
}>()

const mountEl = ref<HTMLDivElement | null>(null)
const statusMessage = ref('3D model is not available for this part.')

let renderer: WebGLRenderer | null = null
let camera: PerspectiveCamera | null = null
let scene: Scene | null = null
let controls: OrbitControls | null = null
let currentModel: Object3D | null = null
let resizeObserver: ResizeObserver | null = null
let frameId = 0
let loadRequestId = 0

const animate = () => {
  if (!renderer || !scene || !camera) {
    return
  }
  controls?.update()
  renderer.render(scene, camera)
  frameId = window.requestAnimationFrame(animate)
}

const syncViewport = () => {
  if (!mountEl.value || !renderer || !camera) {
    return
  }

  const width = Math.max(mountEl.value.clientWidth, 1)
  const height = Math.max(mountEl.value.clientHeight, 1)
  renderer.setSize(width, height)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
}

const fitCameraToObject = (object: Object3D) => {
  if (!camera || !controls) {
    return
  }
  const box = new Box3().setFromObject(object)
  const size = box.getSize(new Vector3()).length() || 1
  const center = box.getCenter(new Vector3())

  camera.position.set(center.x + size, center.y + size, center.z + size)
  camera.near = 0.1
  camera.far = size * 10
  camera.updateProjectionMatrix()

  controls.target.copy(center)
  controls.update()
}

const clearModel = () => {
  if (!scene || !currentModel) {
    return
  }
  scene.remove(currentModel)
  currentModel.traverse((child: any) => {
    child.geometry?.dispose?.()
    if (Array.isArray(child.material)) {
      child.material.forEach((material: any) => material.dispose?.())
    } else {
      child.material?.dispose?.()
    }
  })
  currentModel = null
}

const loadModel = async () => {
  const requestId = ++loadRequestId
  if (!scene || !props.available || !props.wrlUrl) {
    clearModel()
    statusMessage.value = '3D model is not available for this part.'
    return
  }

  const loader = new VRMLLoader()
  clearModel()
  statusMessage.value = 'Loading 3D model...'
  loader.load(
    props.wrlUrl,
    (object) => {
      if (requestId !== loadRequestId) {
        object.traverse((child: any) => {
          child.geometry?.dispose?.()
          if (Array.isArray(child.material)) {
            child.material.forEach((material: any) => material.dispose?.())
          } else {
            child.material?.dispose?.()
          }
        })
        return
      }
      object.rotation.x = -Math.PI / 2
      scene?.add(object)
      currentModel = object
      fitCameraToObject(object)
      statusMessage.value = ''
    },
    undefined,
    () => {
      if (requestId !== loadRequestId) {
        return
      }
      clearModel()
      statusMessage.value = '3D preview could not be loaded.'
    },
  )
}

onMounted(() => {
  if (!mountEl.value) {
    return
  }

  scene = new Scene()
  scene.background = new Color('#f8fafc')

  camera = new PerspectiveCamera(
    45,
    mountEl.value.clientWidth / mountEl.value.clientHeight,
    0.1,
    1000,
  )
  camera.position.set(30, 30, 30)

  renderer = new WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  syncViewport()
  mountEl.value.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  const ambient = new AmbientLight('#ffffff', 1.2)
  const key = new DirectionalLight('#ffffff', 2.4)
  key.position.set(20, 30, 15)

  scene.add(ambient)
  scene.add(key)

  resizeObserver = new ResizeObserver(() => {
    syncViewport()
    if (currentModel) {
      fitCameraToObject(currentModel)
    }
  })
  resizeObserver.observe(mountEl.value)

  animate()
  void loadModel()
})

watch(
  () => [props.available, props.wrlUrl] as const,
  () => {
    void loadModel()
  },
)

onBeforeUnmount(() => {
  loadRequestId += 1
  window.cancelAnimationFrame(frameId)
  clearModel()
  resizeObserver?.disconnect()
  controls?.dispose()
  renderer?.dispose()
})
</script>

<template>
  <div ref="mountEl" class="model-preview">
    <div v-if="statusMessage" class="model-preview__status">
      {{ statusMessage }}
    </div>
  </div>
</template>
