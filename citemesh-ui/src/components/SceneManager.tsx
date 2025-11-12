import { useEffect } from 'react'
import type { RefObject } from 'react'
import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { MeshSurfaceSampler } from 'three/examples/jsm/math/MeshSurfaceSampler.js'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

type SceneManagerProps = {
  canvasRef: RefObject<HTMLCanvasElement | null>
  mainRef: RefObject<HTMLElement | null>
  onReady?: () => void
}

const PARTICLE_COUNT = 10000
const CRYSTAL_RADIUS = 10

const vertexShader = `
  varying vec3 vNormal;
  varying vec3 vViewPosition;
  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vNormal = normalize(normalMatrix * normal);
    vViewPosition = -mvPosition.xyz;
    gl_Position = projectionMatrix * mvPosition;
  }
`

const fragmentShader = `
  uniform vec3 color1;
  uniform vec3 color2;
  uniform float opacity;
  varying vec3 vNormal;
  varying vec3 vViewPosition;
  void main() {
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(vViewPosition);
    float fresnel = 1.0 - dot(normal, viewDir);
    fresnel = pow(fresnel, 2.2);
    vec3 finalColor = mix(color1, color2, fresnel);
    gl_FragColor = vec4(finalColor, opacity * fresnel);
  }
`

const createPaperBodyGeometry = () => {
  const bodyShape = new THREE.Shape()
  bodyShape.moveTo(-0.6, -0.84)
  bodyShape.lineTo(-0.6, 0.82)
  bodyShape.lineTo(0.34, 0.82)
  bodyShape.lineTo(0.6, 0.56)
  bodyShape.lineTo(0.6, -0.84)
  bodyShape.lineTo(-0.6, -0.84)

  const geometry = new THREE.ExtrudeGeometry(bodyShape, {
    depth: 0.16,
    bevelEnabled: true,
    bevelThickness: 0.02,
    bevelSize: 0.02,
    bevelSegments: 2
  })

  geometry.center()
  geometry.scale(9, 9, 9)
  return geometry
}

const createPaperFoldGeometry = () => {
  const foldShape = new THREE.Shape()
  foldShape.moveTo(0.34, 0.82)
  foldShape.lineTo(0.6, 0.56)
  foldShape.lineTo(0.6, 0.82)
  foldShape.lineTo(0.34, 0.82)

  const geometry = new THREE.ExtrudeGeometry(foldShape, {
    depth: 0.12,
    bevelEnabled: true,
    bevelThickness: 0.015,
    bevelSize: 0.015,
    bevelSegments: 2
  })

  geometry.center()
  geometry.scale(9, 9, 9)
  return geometry
}

const SceneManager = ({ canvasRef, mainRef, onReady }: SceneManagerProps) => {
  useEffect(() => {
    const canvas = canvasRef.current
    const main = mainRef.current
    if (!canvas || !main) {
      return undefined
    }

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.setSize(window.innerWidth, window.innerHeight)
    camera.position.set(0, 0, 32)

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.25)
    scene.add(ambientLight)

    const keyLight = new THREE.DirectionalLight(0xf5f3ff, 1.4)
    keyLight.position.set(18, 24, 18)
    scene.add(keyLight)

    const rimLight = new THREE.PointLight(0x8b5cf6, 1.8, 90)
    rimLight.position.set(-16, -12, 20)
    scene.add(rimLight)

    const composer = new EffectComposer(renderer)
    const renderScene = new RenderPass(scene, camera)
    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.4,
      0.4,
      0.85
    )
    bloomPass.threshold = 0
    bloomPass.strength = 1.35
    bloomPass.radius = 0.42
    composer.addPass(renderScene)
    composer.addPass(bloomPass)

    const rootGroup = new THREE.Group()
    scene.add(rootGroup)

    const crystalGroup = new THREE.Group()
    rootGroup.add(crystalGroup)

    const paperGroup = new THREE.Group()
    paperGroup.visible = false
    rootGroup.add(paperGroup)

    const crystalGeom = new THREE.DodecahedronGeometry(CRYSTAL_RADIUS, 1)
    const crystalMaterial = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        color1: { value: new THREE.Color(0x4338ca) },
        color2: { value: new THREE.Color(0xd8b4fe) },
        opacity: { value: 0.0 }
      },
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })
    const crystalMesh = new THREE.Mesh(crystalGeom, crystalMaterial)
    crystalGroup.add(crystalMesh)

    const wireframeGeom = new THREE.WireframeGeometry(crystalGeom)
    const wireframeMaterial = new THREE.LineBasicMaterial({
      color: 0xc084fc,
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })
    const wireframe = new THREE.LineSegments(wireframeGeom, wireframeMaterial)
    crystalGroup.add(wireframe)

    const paperBodyGeom = createPaperBodyGeometry()
    const paperFoldGeom = createPaperFoldGeometry()
    paperBodyGeom.computeBoundingSphere()
    const paperRadius = paperBodyGeom.boundingSphere?.radius ?? 12

    const paperBodyMaterial = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      emissive: new THREE.Color(0x7c3aed).multiplyScalar(0.25),
      metalness: 0.05,
      roughness: 0.15,
      clearcoat: 0.9,
      clearcoatRoughness: 0.2,
      sheen: 0.45,
      sheenColor: new THREE.Color(0xe9d5ff),
      reflectivity: 0.45,
      transparent: true,
      opacity: 0
    })

    const paperFoldMaterial = new THREE.MeshStandardMaterial({
      color: 0xab8bff,
      emissive: new THREE.Color(0x8b5cf6).multiplyScalar(0.4),
      metalness: 0.42,
      roughness: 0.32,
      transparent: true,
      opacity: 0
    })

    const paperEdgeMaterial = new THREE.MeshBasicMaterial({
      color: 0xc4b5fd,
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending
    })

    const paperBody = new THREE.Mesh(paperBodyGeom, paperBodyMaterial)
    const paperFold = new THREE.Mesh(paperFoldGeom, paperFoldMaterial)
    paperFold.position.z = 0.08
    const paperEdge = new THREE.Mesh(paperBodyGeom.clone(), paperEdgeMaterial)
    paperEdge.scale.set(1.006, 1.006, 1.006)
    paperEdge.renderOrder = 1

    paperGroup.add(paperBody, paperFold, paperEdge)
    paperGroup.rotation.set(0, 0, 0)

    const positions = new Float32Array(PARTICLE_COUNT * 3)
    const crystalPositions = new Float32Array(PARTICLE_COUNT * 3)
    const paperPositions = new Float32Array(PARTICLE_COUNT * 3)

    const particlesGeom = new THREE.BufferGeometry()
    const crystalSampler = new MeshSurfaceSampler(new THREE.Mesh(crystalGeom)).build()
    const paperSampler = new MeshSurfaceSampler(new THREE.Mesh(paperBodyGeom)).build()
    const tempVector = new THREE.Vector3()

    for (let i = 0; i < PARTICLE_COUNT; i += 1) {
      const idx = i * 3
      const randomPos = new THREE.Vector3().randomDirection().multiplyScalar(18 + Math.random() * 28)
      positions[idx] = randomPos.x
      positions[idx + 1] = randomPos.y
      positions[idx + 2] = randomPos.z

      crystalSampler.sample(tempVector)
      crystalPositions[idx] = tempVector.x
      crystalPositions[idx + 1] = tempVector.y
      crystalPositions[idx + 2] = tempVector.z

      paperSampler.sample(tempVector)
      paperPositions[idx] = tempVector.x
      paperPositions[idx + 1] = tempVector.y
      paperPositions[idx + 2] = tempVector.z
    }

    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.085,
      color: new THREE.Color(0xdcc0ff),
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })

    particlesGeom.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    particlesGeom.setAttribute('crystalPosition', new THREE.BufferAttribute(crystalPositions, 3))
    particlesGeom.setAttribute('paperPosition', new THREE.BufferAttribute(paperPositions, 3))
    const particles = new THREE.Points(particlesGeom, particlesMaterial)
    rootGroup.add(particles)

    const mouse = new THREE.Vector2()
    const handleMouseMove = (event: MouseEvent) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1
    }
    window.addEventListener('mousemove', handleMouseMove)

    const resizeHandler = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
      composer.setSize(window.innerWidth, window.innerHeight)
    }
    window.addEventListener('resize', resizeHandler)

  const toArray = gsap.utils.toArray<HTMLElement>
    const painPointTweens = gsap.utils.toArray<HTMLElement>('.pain-point').map((point, index) =>
      gsap.fromTo(
        point,
        { opacity: 0, x: -20 },
        {
          opacity: 1,
          x: 0,
          duration: 0.5,
          delay: index * 0.2,
          scrollTrigger: {
            trigger: '#section-2',
            start: 'top center',
            toggleActions: 'play none none reverse'
          }
        }
      )
    )

    const morphParticles = (
      attributeName: 'crystalPosition' | 'paperPosition',
      startArray: Float32Array,
      progress: number
    ) => {
      const positionsAttr = particlesGeom.getAttribute('position') as THREE.BufferAttribute
      const targetAttr = particlesGeom.getAttribute(attributeName) as THREE.BufferAttribute
      for (let i = 0; i < PARTICLE_COUNT; i += 1) {
        const idx = i * 3
        const startX = startArray[idx]
        const startY = startArray[idx + 1]
        const startZ = startArray[idx + 2]
        const targetX = targetAttr.getX(i)
        const targetY = targetAttr.getY(i)
        const targetZ = targetAttr.getZ(i)
        positionsAttr.setXYZ(
          i,
          THREE.MathUtils.lerp(startX, targetX, progress),
          THREE.MathUtils.lerp(startY, targetY, progress),
          THREE.MathUtils.lerp(startZ, targetZ, progress)
        )
      }
      positionsAttr.needsUpdate = true
    }

    const initialPositions = new Float32Array(positions)

    const timeline = gsap.timeline({ paused: true })
    timeline.to(camera.position, { z: 26, ease: 'power2.inOut' }, 0)

    const crystalState = { progress: 0 }
    timeline.to(
      crystalState,
      {
        progress: 1,
        duration: 3.4,
        ease: 'power2.out',
        onUpdate: () => morphParticles('crystalPosition', initialPositions, crystalState.progress)
      },
      0
    )

    timeline.to(crystalMaterial.uniforms.opacity, { value: 1, duration: 2.4, ease: 'power2.out' }, 0.4)
    timeline.to(wireframeMaterial, { opacity: 0.55, duration: 2, ease: 'power2.out' }, 0.6)
    timeline.to(particlesMaterial.color, { r: 0.8, g: 0.56, b: 0.98, duration: 3.4, ease: 'power1.inOut' }, 0)
    timeline.to(crystalGroup.rotation, { y: '+=0.8', duration: 3.4, ease: 'power2.inOut' }, 0)

    const paperState = { progress: 0 }
    let paperStart: Float32Array | null = null
    timeline.to(
      paperState,
      {
        progress: 1,
        duration: 3,
        ease: 'power2.inOut',
        onStart: () => {
          paperGroup.visible = true
          paperStart = new Float32Array((particlesGeom.getAttribute('position') as THREE.BufferAttribute).array as Float32Array)
          
          // Transfer particles from rootGroup to paperGroup with position correction
          const worldPos = new THREE.Vector3()
          particles.getWorldPosition(worldPos)
          rootGroup.remove(particles)
          paperGroup.add(particles)
          paperGroup.worldToLocal(worldPos)
          particles.position.copy(worldPos)
        },
        onUpdate: () => {
          if (!paperStart) return
          morphParticles('paperPosition', paperStart, paperState.progress)
        },
        onComplete: () => {
          crystalGroup.visible = false
          // Reset particle local position to zero since they're now properly parented
          particles.position.set(0, 0, 0)
        }
      },
      3.6
    )

    timeline.to(crystalMaterial.uniforms.opacity, { value: 0, duration: 1.2, ease: 'power1.out' }, 3.6)
    timeline.to(wireframeMaterial, { opacity: 0, duration: 1.2, ease: 'power1.out' }, 3.6)
    timeline.to(paperBodyMaterial, { opacity: 1, duration: 1.6, ease: 'power2.out' }, 3.8)
    timeline.to(paperFoldMaterial, { opacity: 1, duration: 1.6, ease: 'power2.out' }, 3.8)
    timeline.to(paperEdgeMaterial, { opacity: 0.28, duration: 1.6, ease: 'power2.out' }, 3.8)
    timeline.to(paperGroup.position, { y: -2.5, duration: 2.6, ease: 'power2.inOut' }, 3.8)
    timeline.to(particlesMaterial, { opacity: 0.04, duration: 1.6, ease: 'power2.out' }, 3.8)
    timeline.to(camera.position, { z: 31.5, ease: 'power2.out' }, 3.8)

    const lockTime = 6.6
    let hasReachedLockPoint = false
    const timelineDuration = timeline.duration()
    const timelineProgress = gsap.quickTo(timeline, 'progress', {
      duration: 0.45,
      ease: 'power2.out'
    })

    const scrollTimelineTrigger = ScrollTrigger.create({
      trigger: main,
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1.4,
      onUpdate: (self) => {
        let current = self.progress
        const lockProgress = timelineDuration > 0 ? lockTime / timelineDuration : 0
        if (current >= lockProgress) hasReachedLockPoint = true
        if (hasReachedLockPoint && current < lockProgress) current = lockProgress
        timelineProgress(current)
      }
    })

    const cards = gsap.utils.toArray<HTMLElement>('.process-card')
    const connections = cards.map((card) => {
      const lineGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, 0, 0)
      ])
      const lineMaterial = new THREE.LineBasicMaterial({
        color: 0xd8b4fe,
        transparent: true,
        opacity: 0,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      })
      const line = new THREE.Line(lineGeometry, lineMaterial)
      scene.add(line)

      const popInTl = gsap.timeline({ paused: true }).fromTo(
        card,
        { opacity: 0, scale: 0.95, y: 20 },
        {
          opacity: 1,
          scale: 1,
          y: 0,
          boxShadow: '0 0 25px 5px rgba(147, 51, 234, 0.7)',
          duration: 0.5,
          ease: 'power2.out'
        }
      )

      return { card, line, popInTl }
    })

    const processTrigger = ScrollTrigger.create({
      trigger: '#section-3',
      start: 'top 80%',
      end: 'bottom 20%',
      scrub: true,
      onUpdate: () => {
        let activeIndex = -1
        let smallestDist = Infinity
        const triggerPoint = window.innerHeight * 0.4

        connections.forEach((entry, index) => {
          const rect = entry.card.getBoundingClientRect()
          const dist = Math.abs(rect.top - triggerPoint)
          if (rect.top < window.innerHeight && rect.bottom > 0 && dist < smallestDist) {
            smallestDist = dist
            activeIndex = index
          }
        })

        connections.forEach((entry, index) => {
          const rect = entry.card.getBoundingClientRect()
          const progress = gsap.utils.clamp(
            0,
            1,
            gsap.utils.mapRange(window.innerHeight * 0.8, window.innerHeight * 0.3, 0, 1, rect.top)
          )
          entry.popInTl.progress(progress)
          entry.line.material.opacity = index === activeIndex ? progress : 0
        })
      }
    })

    const solutionPanel = document.getElementById('solution-panel')
    const solutionTween = solutionPanel
      ? gsap.fromTo(
          solutionPanel,
          { opacity: 0, y: 50 },
          {
            opacity: 1,
            y: 0,
            duration: 0.7,
            ease: 'power2.out',
            boxShadow: '0 0 25px 5px rgba(147, 51, 234, 0.7)',
            scrollTrigger: {
              trigger: solutionPanel,
              start: 'top 85%',
              toggleActions: 'play none none reverse'
            }
          }
        )
      : null

    const impactTweens = toArray('.impact-number').map((element) => {
      const targetText = element.textContent ?? ''
      const match = targetText.match(/([$]?)([\d,]+)([.]?\d*)?([%M]?)/)
      if (!match) return null

      const prefix = match[1] ?? ''
      const suffix = match[4] ?? ''
      const target = parseFloat((match[2] + (match[3] ?? '')).replace(/,/g, ''))
      const counter = { value: 0 }

      return gsap.to(counter, {
        value: target,
        duration: 2,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: element,
          start: 'top 85%',
          toggleActions: 'play none none reverse'
        },
        onUpdate: () => {
          let displayText = ''
          if (targetText.includes(',')) {
            displayText = Math.round(counter.value).toLocaleString('en-US')
          } else if (targetText.includes('.')) {
            displayText = counter.value.toFixed(1)
          } else {
            displayText = Math.round(counter.value).toString()
          }
          element.textContent = `${prefix}${displayText}${suffix}`
        }
      })
    })

    let activeConnectionGroup: THREE.Group = crystalGroup
    let activeConnectionRadius = CRYSTAL_RADIUS
    timeline.call(() => {
      activeConnectionGroup = paperGroup
      activeConnectionRadius = paperRadius
    }, undefined, 3.6)

    const clock = new THREE.Clock()
    let frameId = 0

    const animate = () => {
      clock.getDelta()
      
      const scrollProgress = timeline.progress()
      const paperMorphComplete = scrollProgress >= (6.6 / timelineDuration)
      
      if (!paperMorphComplete) {
        rootGroup.rotation.y += 0.0006
        rootGroup.rotation.x += 0.0002
      }
      // Paper stays fixed at 90 degrees after morph completes

      const smoothedMouseX = camera.position.x + (mouse.x * 1.6 - camera.position.x) * 0.05
      const smoothedMouseY = camera.position.y + (mouse.y * 1.2 - camera.position.y) * 0.05
      camera.position.x = smoothedMouseX
      camera.position.y = smoothedMouseY
      camera.lookAt(scene.position)

      // Auto-detect text elements and apply localized glow where paper is positioned
      if (paperMorphComplete && paperGroup.visible) {
        const paperWorldPos = new THREE.Vector3()
        paperGroup.getWorldPosition(paperWorldPos)
        
        // Project paper position to screen space
        const paperScreenPos = paperWorldPos.clone().project(camera)
        const paperScreenX = (paperScreenPos.x + 1) * window.innerWidth / 2
        const paperScreenY = (-paperScreenPos.y + 1) * window.innerHeight / 2
        
        // Check all heading elements and their child spans (but exclude purple text)
        const allTextElements = document.querySelectorAll('h1, h2, h3, h1 > span:not(.text-purple-500), h2 > span:not(.text-purple-500), h3 > span:not(.text-purple-500)')
        allTextElements.forEach((element) => {
          // Skip elements that are already purple
          if (element.classList.contains('text-purple-500')) return
          
          const rect = element.getBoundingClientRect()
          
          // Check if paper is overlapping with this text element
          const isOverlapping = paperScreenY >= rect.top - 150 && paperScreenY <= rect.bottom + 150
          
          if (isOverlapping) {
            // Calculate distance from paper center to text center
            const textCenterX = rect.left + rect.width / 2
            const textCenterY = rect.top + rect.height / 2
            const distanceX = paperScreenX - textCenterX
            const distanceY = paperScreenY - textCenterY
            const distance = Math.sqrt(distanceX * distanceX + distanceY * distanceY)
            
            // Calculate glow intensity based on distance (closer = stronger glow)
            const maxGlowDistance = 300 // pixels
            const intensity = Math.max(0, 1 - (distance / maxGlowDistance))
            
            // Apply localized glow with calculated intensity
            const htmlElement = element as HTMLElement
            htmlElement.style.setProperty('--glow-intensity', intensity.toFixed(2))
            
            if (!element.classList.contains('localized-glow')) {
              element.classList.add('localized-glow')
            }
          } else {
            // Paper not overlapping - remove glow
            element.classList.remove('localized-glow')
            ;(element as HTMLElement).style.removeProperty('--glow-intensity')
          }
        })
      }

      const worldCenter = new THREE.Vector3()
      activeConnectionGroup.getWorldPosition(worldCenter)

      connections.forEach((entry) => {
        const progress = entry.popInTl.progress()
        if (progress <= 0) {
          gsap.set(entry.card, { x: 0, y: 0 })
          return
        }

        const parallaxX = -smoothedMouseX * 9
        const parallaxY = -smoothedMouseY * 9
        gsap.set(entry.card, { x: parallaxX, y: parallaxY })

        const rect = entry.card.getBoundingClientRect()
        const cardX = ((rect.left + rect.width / 2) / window.innerWidth) * 2 - 1
        const cardY = -((rect.top + rect.height / 2) / window.innerHeight) * 2 + 1
        const cardWorldPos = new THREE.Vector3(cardX, cardY, 0.5).unproject(camera)

        const surfaceDirection = cardWorldPos.clone().sub(worldCenter).normalize()
        const worldSurfacePoint = worldCenter.clone().add(surfaceDirection.multiplyScalar(activeConnectionRadius))

        const posAttr = entry.line.geometry.attributes.position as THREE.BufferAttribute
        posAttr.setXYZ(0, worldSurfacePoint.x, worldSurfacePoint.y, worldSurfacePoint.z)
        posAttr.setXYZ(1, cardWorldPos.x, cardWorldPos.y, cardWorldPos.z)
        posAttr.needsUpdate = true
      })

      composer.render()
      frameId = requestAnimationFrame(animate)
    }

    animate()

    const readyTimeout = window.setTimeout(() => {
      canvas.classList.add('canvas-visible')
      onReady?.()
    }, 700)

    return () => {
      window.clearTimeout(readyTimeout)
      cancelAnimationFrame(frameId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', resizeHandler)

      painPointTweens.forEach((tween) => tween?.kill())
      impactTweens.forEach((tween) => tween?.kill())
      solutionTween?.kill()
      scrollTimelineTrigger.kill()
      processTrigger.kill()
      timeline.kill()

      ScrollTrigger.getAll().forEach((trigger) => trigger.kill())

      connections.forEach((entry) => {
        scene.remove(entry.line)
        entry.line.geometry.dispose()
        entry.line.material.dispose()
      })

      particlesGeom.dispose()
      particlesMaterial.dispose()
      crystalGeom.dispose()
      crystalMaterial.dispose()
      wireframeGeom.dispose()
      wireframeMaterial.dispose()
      paperBodyGeom.dispose()
      paperFoldGeom.dispose()
      paperBodyMaterial.dispose()
      paperFoldMaterial.dispose()
      paperEdgeMaterial.dispose()

      composer.dispose()
      renderer.dispose()
    }
  }, [canvasRef, mainRef, onReady])

  return <canvas ref={canvasRef} id="bg-canvas" />
}

export default SceneManager
