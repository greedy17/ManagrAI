<template>
  <div ref="root" class="root">
    <div ref="container" class="container">
      <ul class="progress-bar" v-for="(set, i) in setsOfFour" :key="i">
        <li
          class="active"
          v-for="action in set"
          :key="action.title"
          :style="{ '--count': `'${action.count}'` }"
        >
          <span class="title">{{ action.title }}</span>
        </li>
        <li v-for="n in 4 - set.length" :key="n" class="hidden"></li>
      </ul>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ActionsGraphic',
  props: {
    actions: {
      type: Array,
      required: true,
    },
  },
  created() {
    setTimeout(this.configureRoot, 0)
  },
  methods: {
    configureRoot() {
      // Due to styling for the graphics, there are items with position: absolute.
      // But that gets this component out of the document flow.
      // To accomodate these elements, set the height of "root", the parent.
      this.$refs.root.style.height = `${this.$refs.container.offsetHeight}px`
    },
  },
  computed: {
    setsOfFour() {
      let output = []
      let chunk = 4
      for (let i = 0, j = this.actions.length; i < j; i += chunk) {
        let tempArray = this.actions.slice(i, i + chunk)
        output.push(tempArray)
      }

      return output
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.container {
  width: 76vw;
  position: absolute;
  z-index: 1;
}
.progress-bar {
  list-style: none;
  display: flex;
  flex-flow: row;
  justify-content: left;
  margin-top: 2rem;
  padding: 0;
}
.progress-bar li {
  width: 20rem;
  position: relative;
  text-align: center;
  font-size: 2rem;
}
.progress-bar li span.title {
  font-size: 1rem;
}
.progress-bar li:before {
  content: var(--count);
  width: 3rem;
  height: 3rem;
  border: 2px solid #bebebe;
  margin: 0 auto 10px auto;
  border-radius: 50%;
  background: $white;
  color: #bebebe;
  display: flex;
  align-items: center;
  justify-content: center;
}
.progress-bar li:after {
  content: '';
  position: absolute;
  width: 100%;
  height: 0.7rem;
  background: #979797;
  top: 1.25rem;
  left: -50%;
  z-index: -1;
}
.progress-bar li.hidden:after {
  background: rgba($color: $dark-green, $alpha: 0);
}
.progress-bar li.active:before {
  border-color: $yellow;
  background: $white;
  color: $yellow;
}
.progress-bar li.active:after {
  background: $soft-gray;
}
.progress-bar li.active li:after {
  background: $soft-gray;
}
.progress-bar li.active li:before {
  border-color: $soft-gray;
  background: $soft-gray;
  color: $white;
}
.progress-bar li:first-child:after {
  content: none;
}
</style>
