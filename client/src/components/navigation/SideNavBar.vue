<template>
  <div class="sidenav-container">
    <div class="sidenav" ref="sidenav">
      <div class="content">
        <div class="view-toggle-container">
          <span class="left" :class="{ bold: selectedView == remindersView }">Reminders</span>
          <ToggleCheckBox
            class="checkbox"
            :checked="selectedView == notificationsView"
            @toggle-view="toggleView"
            :eventToEmit="'toggle-view'"
          />
          <span class="right" :class="{ bold: selectedView == notificationsView }"
            >Notifications</span
          >
        </div>
        <NotificationPage
          v-if="selectedView == notificationsView"
          @refresh-unviewed-notif-count="$emit('refresh-unviewed-notif-count')"
        />
        <ReminderPage v-if="selectedView == remindersView" />
      </div>
    </div>
  </div>
</template>

<script>
import NotificationPage from '@/views/user/NotificationPage'
import ReminderPage from '@/views/user/ReminderPage'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import { mapGetters } from 'vuex'
const VIEW_OPTION_REMINDERS = 'REMINDERS'
const VIEW_OPTION_NOTIFICATIONS = 'NOTIFICATIONS'
const VIEW_OPTIONS = {
  notifications: VIEW_OPTION_NOTIFICATIONS,
  reminders: VIEW_OPTION_REMINDERS,
}
export default {
  name: 'SideNavBar',
  components: { NotificationPage, ToggleCheckBox, ReminderPage },
  props: {},
  data() {
    return {
      triggerElements: [],
      viewOptions: VIEW_OPTIONS,
      remindersView: VIEW_OPTION_REMINDERS,
      notificationsView: VIEW_OPTION_NOTIFICATIONS,
      selectedView: VIEW_OPTION_NOTIFICATIONS,
    }
  },
  methods: {
    toggleView(event) {
      if (event) {
        this.selectedView = this.viewOptions.notifications
      } else {
        this.selectedView = this.viewOptions.reminders
      }
    },
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
  top: 5rem;
  width: 0rem;
  max-width: 15rem;
  min-height: 90%;
  > .content {
    display: none;
  }
}

.sidenav.close {
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
    width: 15rem;
  }
}
@keyframes closemenu {
  0% {
    width: 15rem;
    background-color: transparent;
  }
  50% {
    background-color: lighten($soft-gray, 2%);
  }

  100% {
    width: 0vw;
    background-color: lighten($soft-gray, 5%);
  }
}
.view-toggle-container {
  display: flex;
  justify-content: space-between;
}
.bold {
  font-weight: bold;
}
</style>
