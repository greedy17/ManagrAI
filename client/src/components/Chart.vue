<template>
  <section class="column">
    <div class="container">
      <div class="donut-chart-block block">
        <div class="donut-chart">
          <div id="part1" class="portion-block"><div class="circle"></div></div>
          <div id="part2" class="portion-block"><div class="circle"></div></div>
          <div id="part3" class="portion-block"><div class="circle"></div></div>
          <p class="center"></p>
        </div>
      </div>
    </div>
    <!-- <div class="labels">
      <p><img class="w-green" src="@/assets/images/square.svg" height="12px" alt="" />Factor 1</p>
      <p><img class="w-green" src="@/assets/images/square.svg" height="12px" alt="" />Factor 2</p>
      <p><img class="w-green" src="@/assets/images/square.svg" height="12px" alt="" />Factor 3</p>
    </div> -->
  </section>
</template>

<script>
export default {
  name: 'Chart',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.labels {
  font-size: 11px;
  p {
    display: flex;
    flex-direction: row;
    align-items: center;
  }
}
.w-green {
  filter: invert(83%) sepia(28%) saturate(135%) hue-rotate(92deg) brightness(111%) contrast(95%);
  margin-right: 4px;
}
* {
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}

.donut-chart {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 1rem;
  border-radius: 100%;
}
p.center {
  background: white;
  color: $yellow;
  position: absolute;
  text-align: center;
  font-size: 28px;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  width: 130px;
  height: 130px;
  margin: auto;
  border-radius: 50%;
  line-height: 35px;
  padding: 20% 0 0;
}

.portion-block {
  border-radius: 50%;
  clip: rect(0px, 200px, 200px, 100px);
  height: 100%;
  position: absolute;
  width: 100%;
}
.circle {
  border-radius: 50%;
  clip: rect(0px, 100px, 200px, 0px);
  height: 100%;
  position: absolute;
  width: 100%;
  font-family: monospace;
  font-size: 1.5rem;
}

#part1 {
  transform: rotate(0deg);
}

#part1 .circle {
  background-color: $dark-green;
  /*transform: rotate(76deg);*/
  animation: first 1s 1 forwards;
}

#part2 {
  transform: rotate(100deg);
}
#part2 .circle {
  background-color: $dark-green;
  animation: second 1s 1 forwards 1s;
}
#part3 {
  transform: rotate(250deg);
}
#part3 .circle {
  background-color: white;
  animation: third 0.5s 1 forwards 2s;
}

/* Animation */
@keyframes first {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(100deg);
  }
}

@keyframes second {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(150deg);
  }
}

@keyframes third {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(111deg);
  }
}
</style>