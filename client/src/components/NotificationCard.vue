<template>
  <div class="notificaion-container">
    <div class="notification-card" :class="{ unviewed: !notification.viewed }">
      <div class="notification-card__title">
        <span @click="toggleCard" class="notification-card__title__text">{{
          notification.title
        }}</span>
        <span class="notification-card__title__type">
          <svg class="icon-notification">
            <use :xlink:href="require('@/assets/images/svg-repo.svg') + '#' + notificationIcon" />
          </svg>
        </span>
      </div>
      <div class="notification-card__content" :class="{ expand: expand }">
        {{ notification.meta ? notification.meta.content : '' }}
        <div
          @click.prevent="goToLead(lead.id)"
          :key="lead.id"
          v-for="lead in notification.meta.leads"
          class="notification-card__content__leads"
        >
          {{ lead.title }}
        </div>
      </div>
      <div class="notification-card__footer" :class="{ expand: expand }">
        <span class="notification-card__footer__type">
          {{ notification.notificationType }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { NOTIFICATION_TYPES } from '@/services/notifications/'

export default {
  name: 'NotificationCard',
  props: {
    notification: {
      type: [Object, null],
      default: null,
    },
  },
  computed: {
    notificationIcon() {
      switch (this.notification.notificationType) {
        case NOTIFICATION_TYPES.email:
          return 'email'
        case NOTIFICATION_TYPES.reminder:
          return 'alarm'
        case NOTIFICATION_TYPES.system:
          return 'alarm'
        default:
          return 'alarm'
      }
    },
    showSideNav() {
      return this.$store.getters.showSideNav
    },
  },
  data() {
    return {
      expand: false,
      notificationTypes: NOTIFICATION_TYPES,
    }
  },
  methods: {
    toggleNotifications() {
      this.$store.commit('TOGGLE_SIDE_NAV', !this.showSideNav)
    },
    toggleCard() {
      this.expand = !this.expand
      if (!this.notification.viewed) {
        this.$emit('mark-as-viewed', this.notification.id)
      }
    },

    goToLead(id) {
      // avoid redundant route redirect if on current page
      this.toggleNotifications()
      if (this.$route.path !== `/leads/${id}`) {
        this.$router.push({ name: 'LeadsDetail', params: { id: id } })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/sidebars';
@import '@/styles/variables';
.notification-card {
  @include card();
  &:hover {
    cursor: pointer;
  }
  &__title {
    display: flex;
    overflow: hidden;

    &__text {
      flex: 1 0 auto;
    }
    &__type {
    }
  }
  &__content {
    display: none;
    justify-content: center;
    flex-direction: column;
    overflow: hidden;
    &__leads {
      display: flex;
      justify-content: flex-end;
    }
  }
  &__footer {
    display: none;
    justify-content: flex-end;

    &__type {
      color: darken($soft-gray, 15%);
    }
  }
}
.expand {
  display: flex;
}
.icon-notification {
  width: 25px;
  height: 20px;
}
.unviewed {
  background-color: $item-active;
}
</style>
