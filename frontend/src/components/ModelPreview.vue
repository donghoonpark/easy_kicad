<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  AmbientLight,
  Box3,
  Color,
  DirectionalLight,
  Group,
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

let renderer: WebGLRenderer | null = null
let camera: PerspectiveCamera | null = null
let scene: Scene | null = null
let controls: OrbitControls | null = null
let currentModel: Group | null = null
let frameId = 0

const animate = () => {
  if (!renderer || !scene || !camera) {
    return
  }
  controls?.update()
  renderer.render(scene, camera)
  frameId = window.requestAnimationFrame(animate)
}

const fitCameraToObject = (object: Group) => {
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
  if (!scene || !props.available || !props.wrlUrl) {
    clearModel()
    return
  }

  const loader = new VRMLLoader()
  clearModel()
  loader.load(
    props.wrlUrl,
    (object) => {
      object.rotation.x = -Math.PI / 2
      scene?.add(object)
      currentModel = object
      fitCameraToObject(object)
    },
    undefined,
    () => {
      clearModel()
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
  renderer.setSize(mountEl.value.clientWidth, mountEl.value.clientHeight)
  mountEl.value.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  const ambient = new AmbientLight('#ffffff', 1.2)
  const key = new DirectionalLight('#ffffff', 2.4)
  key.position.set(20, 30, 15)

  scene.add(ambient)
  scene.add(key)

  animate()
  void loadModel()
})

watch(
  () => props.wrlUrl,
  () => {
    void loadModel()
  },
)

watch(
  () => props.available,
  () => {
    void loadModel()
  },
)

onBeforeUnmount(() => {
  window.cancelAnimationFrame(frameId)
  clearModel()
  controls?.dispose()
  renderer?.dispose()
})
</script>

<template>
  <div v-if="available" ref="mountEl" class="model-preview" />
  <div v-else class="model-preview model-preview--empty">
    3D model is not available for this part.
  </div>
</template>
