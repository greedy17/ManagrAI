<template>
  <div>
    <div class="lds-ring">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div>
    <p>{{ loaderText }}</p>
  </div>
</template>

<script>
export default {
  name: 'PipelineLoader',
  props: {
    loaderText: String,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

p {
  font-size: 0.8em;
  font-weight: 300;
  margin-top: 5px;
  letter-spacing: 1px;
  color: rgb(82, 82, 82);
}

.lds-ring {
  display: inline-block;
  position: relative;
  width: 2rem;
  height: 2rem;
}
.lds-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 32px;
  height: 32px;
  margin: 4px;
  border: 4px solid $dark-green;
  border-radius: 50%;
  animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: $dark-green transparent transparent transparent;
}
.lds-ring div:nth-child(1) {
  animation-delay: -0.45s;
}
.lds-ring div:nth-child(2) {
  animation-delay: -0.3s;
}
.lds-ring div:nth-child(3) {
  animation-delay: -0.15s;
}
@keyframes lds-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>