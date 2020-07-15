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
      menuItems: [{ name: 'config', options: [{ name: 'config', options: [] }] }],
    }
  },
  methods: {
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
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
}

.sidenav.close {
  background-color: lighten($soft-gray, 5%);
  animation: closemenu forwards;
  animation-duration: 2s;
  animation-iteration-count: 1;
  > .content {
    display: block;
    animation: togglecontent backwards;
    animation-duration: 2s;
    animation-iteration-count: 1;
    animation-direction: reverse;
  }
}

.sidenav.expanded {
  @include standard-border();
  background-color: lighten($soft-gray, 5%);
  animation: expandmenu forwards;
  animation-duration: 1.5s;
  animation-iteration-count: 1;

  > .content {
    display: block;
    animation: togglecontent forwards;
    animation-duration: 1.5s;
    animation-iteration-count: 1;
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
    opacity: 100%;
  }

  100% {
    opacity: 0%;
    width: 0vw;
  }
}
@keyframes togglecontent {
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
</style>
