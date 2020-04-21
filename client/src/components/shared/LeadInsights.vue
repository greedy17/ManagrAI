<template>
  <div class="insights">
    <div class="insights-header section-shadow">
      <span class="insights-header-title">Insights</span>
      <div class="insights-header-link-container">
        <router-link :to="{ name: 'LeadsDetail', params: { id: lead.id } }" v-if="showLink">
          <span class="insights-header-link">See Lead Detail</span>
        </router-link>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/telephone.svg" alt="telephone icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          4 Calls
        </span>
        <span class="insight-bottom">
          3 mins ago
        </span>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/email.svg" alt="email icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          9 Emails
        </span>
        <span class="insight-bottom">
          Yesterday
        </span>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/message.svg" alt="message icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          03/01/20
        </span>
        <span class="insight-bottom">
          Last Action
        </span>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/contact.svg" alt="contact icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          03/01/20
        </span>
        <span class="insight-bottom">
          Contact Update
        </span>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/calendar.svg" alt="calendar icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          0 Demos
        </span>
        <span class="insight-bottom">
          N/A
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeadInsights',
  props: {
    lead: Object,
    showLink: Boolean,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.insights {
  width: 16rem;
  height: 21rem;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
}

.insights-header {
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.insights-header-title {
  flex-grow: 1;
  padding: 5% 0 5% 7%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.insights-header-link-container {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.insights-header-link {
  @include pointer-on-hover();
  text-transform: uppercase;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: $dark-green;

  &:hover {
    border-radius: 5px;
    padding: 0.25rem 0.375rem;
    background-color: $dark-green;
    color: $white;
  }
}

.insight-container {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;
}

.insight-info {
  display: flex;
  flex-flow: column;
  flex-grow: 1;
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
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.insight-bottom {
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: rgba($color: $main-font-gray, $alpha: 0.4);
}

a {
  text-decoration: none;
}
</style>
