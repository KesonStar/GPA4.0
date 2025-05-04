

# 如何实现3D模型背景透明

本教程仅介绍如何让3D模型在右半部分显示时，背景为透明。

## 1. HTML 部分

确保3D模型渲染的容器存在：


## 2. CSS 部分

让3D区域填满父容器且无背景色：

```css
#modelViewer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* 不设置背景色，保持透明 */
}
```

## 3. JavaScript 部分（Three.js）

Three.js 渲染器设置透明背景的关键代码：

```js
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); // alpha: true 允许透明
renderer.setClearColor(0x000000, 0); // 第二个参数为0，表示完全透明
container.appendChild(renderer.domElement);
```

- `alpha: true` 让 WebGL 画布支持透明。
- `setClearColor(0x000000, 0)` 设置背景为完全透明。

## 总结

只需在 Three.js 渲染器初始化时设置 `alpha: true`，并用 `setClearColor(..., 0)`，再配合 CSS 不设置背景色，即可让3D模型背景透明。 