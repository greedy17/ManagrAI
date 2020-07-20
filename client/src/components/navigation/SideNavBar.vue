<template>
  <div class="sidenav-container">
    <div class="background"></div>
    <div class="sidenav" ref="sidenav">
      <div class="content">
        <NotificationPage />
      </div>
    </div>
  </div>
</template>

<script>
import NotificationPage from '@/views/user/NotificationPage'
import { mapGetters } from 'vuex'
export default {
  name: 'SideNavBar',
  components: { NotificationPage },
  props: {},
  data() {
    return {
      triggerElements: [],
    }
  },
  methods: {
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
    },
    removeEvent() {
      /*
        Remove the event listener if the toggle is no longer visible to reduce the events triggered
        */

      return window.removeEventListener('click', this.closeNavBarEvent)
    },
    closeNavBarEvent(e) {
      /** Function to be executed when any click occurs
       * if the click is on the side-nav or on any of its triggers then
       * do not close the modal
       */
      for (let i = 0; i < this.triggerElements.length; i++) {
        if (!this.triggerElements[i].contains(e.target) && !this.$el.contains(e.target)) {
          // if the modal is hidden remove the event listener
          this.removeEvent()
          this.$store.commit('TOGGLE_SIDE_NAV', false)
        }
      }
    },
  },
  computed: {
    ...mapGetters(['showSideNav', 'listenToSideNav']),
    show() {
      return this.showSideNav
    },
  },
  mounted() {
    // gathering all refs that have been defined as triggers
    // when these items are clicked it will consider the click as part
    // of the notifications div
    let children = this.$parent.$children
      .filter(e => e.$refs['notification-trigger'])
      .map(v => {
        return v.$refs['notification-trigger']
      })

    this.triggerElements = children.length > 0 ? [...children] : []

    if (this.show) {
      this.$refs.sidenav.classList.remove('close')
      this.$refs.sidenav.classList.add('expanded')
    } else {
      this.$refs.sidenav.classList.remove('expanded')
    }
  },
  watch: {
    show: {
      immediate: true,
      handler(val) {
        if (val) {
          window.addEventListener('click', this.closeNavBarEvent)
        }
        if (this.$refs.sidenav) {
          if (val) {
            this.$refs.sidenav.classList.remove('close')
            this.$refs.sidenav.classList.add('expanded')
            this.$store.commit('TOGGLE_SIDE_NAV_LISTENER', true)
          } else {
            this.$refs.sidenav.classList.remove('expanded')
            this.$refs.sidenav.classList.add('close')
          }
        }
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers.scss';
@import '@/styles/variables';
.sidenav {
  padding: 1rem;
  background-color: transparent;
  position: absolute;
  right: 0px;
  top: 4rem;
  width: 0rem;
  max-width: 15vw;
  min-height: 92vh;
  > .content {
    display: none;
  }
}

.sidenav.close {
  background-color: lighten($soft-gray, 5%);
  animation: closemenu forwards;
  animation-duration: 1s;
  animation-iteration-count: 1;
  > .content {
    display: none;
  }
}

.sidenav.expanded {
  @include standard-border();
  background-color: lighten($soft-gray, 5%);
  animation: expandmenu forwards;
  animation-duration: 1s;
  animation-iteration-count: 1;

  > .content {
    display: block;
  }
}

@keyframes expandmenu {
  0% {
    width: 0rem;
  }
  100% {
    width: 15vw;
  }
}
@keyframes closemenu {
  0% {
    width: 15vw;
  }

  100% {
    width: 0vw;
  }
}
</style>
