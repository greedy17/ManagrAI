<template>
  <div class="insights">
    <div class="insights-header section-shadow" @click="expandInsights">
      Insights
      <span class="icon__container">
        <svg
          v-if="!showInsights"
          class="icon--unclicked"
          fill="black"
          width="24px"
          height="24px"
          viewBox="0 0 30 30"
        >
          <use xlink:href="@/assets/images/svg-repo.svg#caret" />
        </svg>
        <svg
          v-if="showInsights"
          class="icon--clicked"
          fill="black"
          width="24px"
          height="24px"
          viewBox="0 0 30 30"
        >
          <use xlink:href="@/assets/images/svg-repo.svg#caret" />
        </svg>
      </span>
    </div>

    <div v-show="showInsights">
      <div class="insight-container section-shadow" v-if="refreshedOnce && apiFailing">
        <div style="padding: 1rem;">
          <p>We're having trouble fetching insights for this lead. Please try again later.</p>
        </div>
      </div>

      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/telephone.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.calls.count }}
            {{ 'Call' | pluralize(insights.calls.count) }}
          </span>
          <span class="insight-bottom">{{ insights.calls.latest | timeAgo }}</span>
        </div>
      </div>

      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/pencil.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.notes.count }}
            {{ 'Note' | pluralize(insights.notes.count) }}
          </span>
          <span class="insight-bottom">{{ insights.notes.latest | timeAgo }}</span>
        </div>
      </div>
      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/alarm.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.reminders.count }}
            {{ 'Reminder' | pluralize(insights.reminders.count) }}
          </span>
          <span class="insight-bottom">{{ insights.reminders.latest | timeAgo }}</span>
        </div>
      </div>

      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/checkmark.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.actions.count }}
            {{ 'Action' | pluralize(insights.actions.count) }}
          </span>
          <span class="insight-bottom">{{ insights.actions.latest | timeAgo }}</span>
        </div>
      </div>

      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/email.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.emails.count }}
            {{ 'Email' | pluralize(insights.emails.count) }}
          </span>
          <span class="insight-bottom">{{ insights.emails.latest | timeAgo }}</span>
        </div>
      </div>

      <div class="insight-container section-shadow" v-if="insights && !apiFailing">
        <div class="icon-container">
          <img class="insight-icon" src="@/assets/images/messages.svg" alt="icon" />
        </div>
        <div class="insight-info">
          <span class="insight-top">
            {{ insights.messages.count }}
            {{ 'Message' | pluralize(insights.messages.count) }}
          </span>
          <span class="insight-bottom">{{ insights.messages.latest | timeAgo }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LeadActivityLog from '@/services/leadActivityLogs'

const POLLING_INTERVAL = 2000

export default {
  name: 'LeadInsights',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      insights: null,
      refreshedOnce: false,
      apiFailing: false,
      showInsights: false,
    }
  },
  created() {
    this.refresh(POLLING_INTERVAL)
  },
  destroyed() {
    clearTimeout(this.pollingTimeout)
  },
  methods: {
    refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      LeadActivityLog.api
        .getInsights({
          filters: {
            leads: [this.lead.id],
          },
          enable400Alert: false,
          enable500Alert: false,
        })
        .then(result => {
          this.insights = result
          this.apiFailing = false
          if (repeat) {
            this.pollingTimeout = setTimeout(() => this.refresh(POLLING_INTERVAL), repeat)
          }
        })
        .catch(() => {
          this.apiFailing = true
          if (repeat) {
            // Repeat with exponential back-off as long as calls are failing
            this.pollingTimeout = setTimeout(() => this.refresh(repeat * 2), repeat * 2)
          }
        })
        .finally(() => {
          this.refreshedOnce = true
        })
    },
    expandInsights() {
      this.showInsights = !this.showInsights
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.insights {
  height: auto;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
}

.insights-header {
  @include base-font-styles();
  height: 3rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  padding: 0 10%;
  font-size: 0.875rem;
  font-weight: bold;
  line-height: 1.14;
  color: $main-font-gray;

  &:hover {
    cursor: pointer;
  }
}

.insight-container {
  display: flex;
  flex-flow: row;
  align-items: center;
}

.insight-info {
  display: flex;
  flex-flow: column;
  flex-grow: 1;
  padding: 1rem 0;
}

.icon-container {
  width: 30%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.insight-icon {
  height: 1.25rem;
  width: 1.25rem;
}

.insight-top {
  @include base-font-styles();
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.insight-bottom {
  @include base-font-styles();
  font-size: 14px;
  line-height: 1.14;
  color: rgba($color: $main-font-gray, $alpha: 0.4);
}

a {
  text-decoration: none;
}

.icon {
  &__container {
    display: flex;
  }
  &--unclicked {
    transform: rotate(-90deg);
  }
  &--clicked {
    transform: rotate(90deg);
  }
}
</style>
