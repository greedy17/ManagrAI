<template>
  <div class="loader-wrapper">
    <!-- <div class="loader-2">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div> -->
    <div class="invert">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 7rem" alt="" />
    </div>

    <p>{{ loaderText }}</p>
  </div>
</template>

<script>
export default {
  name: 'Loader',
  props: {
    loaderText: String,
  },
}
</script>

<style scoped>
p {
  font-size: 0.8em;
  font-weight: 300;
  margin-top: 5px;
  letter-spacing: 1px;
  color: rgb(82, 82, 82);
}

.loader-wrapper {
  text-align: center;
  margin-top: 30vh;
}

.loader-2 {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}
.loader-2 div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 64px;
  height: 64px;
  margin: 8px;
  border: 8px solid #199e54;
  border-radius: 50%;
  animation: loader 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #199e54 transparent transparent transparent;
}
.loader-2 div:nth-child(1) {
  animation-delay: -0.45s;
}
.loader-2 div:nth-child(2) {
  animation-delay: -0.3s;
}
.loader-2 div:nth-child(3) {
  animation-delay: -0.15s;
}
@keyframes loader {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>