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
    return {}
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
      if (!this.$el.contains(e.target)) {
        this.$store.commit('TOGGLE_SIDE_NAV', false)
      }

      // this.removeEvent()
      // this.$store.commit('TOGGLE_SIDE_NAV', false)

      // helper to close navbar on click outside of element
    },
  },
  computed: {
    ...mapGetters(['showSideNav']),
    show() {
      return this.showSideNav
    },
  },
  mounted() {
    if (this.show) {
      this.$refs.sidenav.classList.remove('close')
      this.$refs.sidenav.classList.add('expanded')
    } else {
      this.$refs.sidenav.classList.remove('expanded')
    }
  },
  created() {
    // add the eventlistener to the $el click to hide when the click is outside of its el
  },
  watch: {
    show: {
      immediate: false,
      handler(val) {
        if (this.$refs.sidenav) {
          if (val) {
            this.$refs.sidenav.classList.remove('close')
            this.$refs.sidenav.classList.add('expanded')
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
  animation-duration: 1.5s;
  animation-iteration-count: 1;
  > .content {
    display: block;
    animation: hidecontent forwards;
    animation-duration: 1.5s;
    animation-iteration-count: 1;
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
    animation: showcontent forwards;
    animation-duration: 1s;
    animation-iteration-count: 1;
  }
}

@keyframes expandmenu {
  0% {
    width: 0rem;
  }
  100% {
    width: 15vw;
    opacity: 100%;
  }
}
@keyframes closemenu {
  0% {
    width: 15vw;
    opacity: 100%;
  }

  100% {
    opacity: 0%;
    width: 0vw;
  }
}
@keyframes showcontent {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 10%;
  }
  70% {
    opacity: 70%;
  }
  100% {
    opacity: 80%;
  }
}
@keyframes hidecontent {
  0% {
    opacity: 100%;
  }
  50% {
    opacity: 80%;
  }
  70% {
    opacity: 40%;
  }
  100% {
    opacity: 0%;
    display: none;
  }
}
</style>
