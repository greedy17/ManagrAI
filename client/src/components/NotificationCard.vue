<template>
  <div class="notificaion-container">
    <div @click="expand = !expand" class="notification-card">
      <div class="notification-card__title">
        <span class="notification-card__title__text">{{ notification.title }}</span>
        <span class="notification-card__title__type">
          <svg class="icon__clock">
            <use xlink:href="@/assets/images/clock.svg#clock" />
          </svg>
        </span>
      </div>
      <div class="notification-card__content" :class="{ expand: expand }">
        {{ notification.meta ? notification.meta.content : '' }}
        <div
          :key="lead.id"
          v-for="(lead, i) in notification.meta.leads"
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
  data() {
    return {
      expand: false,
      notificationTypes: NOTIFICATION_TYPES,
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/sidebars';
@import '@/styles/variables';
.notification-card {
  @include card();
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
.icon__clock {
  width: 15px;
  height: 15px;
}
</style>
