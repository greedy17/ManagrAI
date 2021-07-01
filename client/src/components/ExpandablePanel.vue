<template>
  <div class="expandable-panel">
    <div class="box">
      <template>
        <slot name="panel-header" :classes="'box__header'" :expand="expandDiv">
          <div @click.prevent="expandDiv" class="box__header">
            {{ title }}
          </div>
        </slot>

        <div ref="panel-content" class="box__content">
          <slot name="panel-content"></slot>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExpandablePanel',
  props: {
    title: { type: String },
  },
  data() {
    return {
      toggling: false,
      isExpanded: false,
    }
  },
  computed: {},
  watch: {
    isExpanded: {
      immediate: true,
      handler(val) {
        if (val) {
          window.addEventListener('click', this.closeEvent)
        }
      },
    },
  },
  methods: {
    onExpandDiv() {
      /**
       * handler for slot
       */
      this.expandDiv()
    },
    expandDiv() {
      /** This Toggle Method handles the classes note the setTimeout must be set to match the animation time */

      let classList = this.$refs['panel-content'].classList
      if (classList.contains('box__content--expanded')) {
        classList.toggle('box__content--closed')
        classList.toggle('box__content--expanded')
        setTimeout(() => {
          classList.remove('box__content--closed')
        }, 200)
        this.isExpanded = false
      } else if (classList.contains('box__content--closed')) {
        classList.toggle('box__content--expanded')
        classList.toggle('box__content--closed')
        this.isExpanded = true
      } else {
        classList.toggle('box__content--expanded')
        this.isExpanded = true
      }
    },
    removeEvent() {
      window.removeEventListener('click', this.closeEvent)
    },
    closeEvent(e) {
      if (this.$el.contains(e.target) || this.$el.contains(e.target.parentNode)) {
        return
      }
      let el = this.$refs['panel-content']
      if (el) {
        let classList = this.$refs['panel-content'].classList
        if (classList.contains('box__content--expanded')) {
          classList.toggle('box__content--closed')
          classList.toggle('box__content--expanded')
          setTimeout(() => {
            classList.remove('box__content--closed')
          }, 200)
        }
      }
      this.isExpanded = false
      this.removeEvent()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/buttons';
@import '@/styles/mixins/utils';
.box {
  border-radius: 0.5rem;
  border: none;
}
.box__header {
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  @include standard-border();
}
.box__content {
  display: none;
}
.box__content--expanded {
  @include standard-border();
  margin-top: 1rem;
  border-radius: 0.5rem;
  display: block;
  animation: expandmenu forwards;
  animation-duration: 1s;
  animation-iteration-count: 1;
}
.box__content--closed {
  @include standard-border();

  display: block;
  animation: closemenu forwards;
  animation-duration: 1s;
  animation-iteration-count: 1;
}
@keyframes expandmenu {
  0% {
    opacity: 0;
    transform: translateY(-10%);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes closemenu {
  0% {
    transform: translateY(0);
    opacity: 0.5;
  }
  100% {
    transform: translateY(-10%);
    opacity: 0;
  }
}
</style>
