<template>
  <div>
    <nav>
      <img src="/logo.png" />
      <span class="managr">
        managr
      </span>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'NavBar',
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Quicksand&display=swap');

nav {
  display: flex;
  align-items: center;
}

img {
  width: 40px;
  height: 40px;
}

.managr {
  width: 111px;
  height: 35px;
  font-family: Quicksand;
  font-size: 24px;
  font-weight: 500;
  font-stretch: normal;
  font-style: normal;
  line-height: normal;
  // letter-spacing: 0.8px;
  // text-align: center;
  color: #199e54;
}
</style>
