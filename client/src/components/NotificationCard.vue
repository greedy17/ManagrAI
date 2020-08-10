<template>
  <div class="notificaion-container">
    <div class="notification-card" :class="{ unviewed: !notification.viewed }">
      <div class="notification-card__title">
        <span @click="toggleCard" class="notification-card__title__text">
          {{ notification.notificationType !== 'EMAIL_OPENED' ? notification.title : 'Read' }}</span
        >
        <span class="notification-card__title__type">
          <svg class="icon-notification">
            <use :xlink:href="require('@/assets/images/svg-repo.svg') + '#' + notificationIcon" />
          </svg>
        </span>
      </div>
      <div class="notification-card__content" :class="{ expand: expand }">
        <span class="muted">
          {{ notification.notifyAt | dateShortWithTime }}
        </span>
        {{ notification.meta ? notification.meta.content : '' }}
        <template v-if="notification.meta">
          <div
            @click.prevent="goToLead(lead.id)"
            :key="lead.id + '-' + i"
            v-for="(lead, i) in notification.meta.leads"
            class="notification-card__content__leads"
          >
            {{ lead.title }}
          </div>
        </template>
        <template v-else>
          {{ notification }}
        </template>
      </div>
      <div class="notification-card__footer" :class="{ expand: expand }">
        <span class="notification-card__footer__type">
          {{ formattedNotificationType.toUpperCase() }}
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
      type: Object,
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
        case NOTIFICATION_TYPES.message:
          return 'sms'
        case NOTIFICATION_TYPES.emailOpened:
          return 'checkmark'
        default:
          return 'alarm'
      }
    },
    formattedNotificationType() {
      switch (this.notification.notificationType) {
        case NOTIFICATION_TYPES.email:
          return 'email'
        case NOTIFICATION_TYPES.message:
          return 'message'
        case NOTIFICATION_TYPES.reminder:
          return 'reminder'
        case NOTIFICATION_TYPES.system:
          return 'system'
        case NOTIFICATION_TYPES.emailOpened:
          return 'email'
        default:
          return 'system'
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
      let nextRoute = this.$router.resolve({ name: 'LeadsDetail', params: { id: id } }).route
      // avoid redundant route redirect if on current page
      if (this.$route.path !== nextRoute.path) {
        this.$router.push({ params: nextRoute.params, name: nextRoute.name })
      }

      this.toggleNotifications()
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
    justify-content: space-between;
    text-transform: capitalize;

    &__text {
      max-width: 12vw;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
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
