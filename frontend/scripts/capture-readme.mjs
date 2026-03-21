import { spawn } from 'node:child_process'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

import { chromium } from 'playwright'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const frontendDir = path.resolve(__dirname, '..')
const repoRoot = path.resolve(frontendDir, '..')
const outputPath = path.join(repoRoot, 'docs', 'assets', 'easy_kicad-ui.png')

const serverPort = Number.parseInt(process.env.EASY_KICAD_SCREENSHOT_PORT ?? '8765', 10)
const screenshotDelayMs = Number.parseInt(process.env.EASY_KICAD_SCREENSHOT_DELAY_MS ?? '3500', 10)
const headless = process.env.EASY_KICAD_SCREENSHOT_HEADLESS === 'true'
const baseUrl = `http://127.0.0.1:${serverPort}`
const appUrl = `${baseUrl}/?capture=readme`

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function waitForServer(url, timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs

  while (Date.now() < deadline) {
    try {
      const response = await fetch(url)
      if (response.ok) {
        return
      }
    } catch {
      // Keep polling until the server is ready.
    }

    await sleep(500)
  }

  throw new Error(`Timed out waiting for ${url}`)
}

async function createScreenshot() {
  await mkdir(path.dirname(outputPath), { recursive: true })

  const browser = await chromium.launch({
    headless,
    args: [
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--use-angle=swiftshader',
    ],
  })

  try {
    const page = await browser.newPage({
      viewport: {
        width: 1440,
        height: 1100,
      },
      deviceScaleFactor: 2,
    })

    await page.goto(appUrl, { waitUntil: 'networkidle' })
    await page.locator('#lcsc-id input').fill('C2040')
    await page.getByRole('button', { name: 'Preview' }).click()

    await page.locator('.part-summary').waitFor({ timeout: 30_000 })
    await page.waitForFunction(() => {
      const status = document.querySelector('.model-preview__status')
      return !status
    }, { timeout: 30_000 })

    await page.waitForTimeout(screenshotDelayMs)

    await page.locator('.app-shell').screenshot({
      path: outputPath,
      type: 'png',
    })
  } finally {
    await browser.close()
  }
}

async function main() {
  const server = spawn(
    'uv',
    ['run', 'easy-kicad', '--serve-only', '--port', String(serverPort)],
    {
      cwd: repoRoot,
      env: {
        ...process.env,
        UV_CACHE_DIR: process.env.UV_CACHE_DIR ?? '.uv-cache',
      },
      stdio: 'inherit',
    },
  )

  try {
    await waitForServer(`${baseUrl}/api/settings`)
    await createScreenshot()
  } finally {
    server.kill('SIGTERM')
    await new Promise((resolve) => server.once('exit', resolve))
  }
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
