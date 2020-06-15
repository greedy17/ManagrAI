<template>
  <div class="insights">
    <div class="insights-header section-shadow">
      Insights
    </div>
    <!-- hiding these as they are still WIP --- as requested by Marcy pb 05/15/20 
  
     <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/telephone.svg" alt="icon" />
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
        <img class="insight-icon" src="@/assets/images/sms.svg" alt="icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          4 Texts
        </span>
        <span class="insight-bottom">
          1/14/20
        </span>
      </div>
    </div>
    <div class="insight-container section-shadow">
      <div class="icon-container">
        <img class="insight-icon" src="@/assets/images/email.svg" alt="icon" />
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
        <img class="insight-icon" src="@/assets/images/message.svg" alt="icon" />
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
        <img class="insight-icon" src="@/assets/images/calendar.svg" alt="icon" />
      </div>
      <div class="insight-info">
        <span class="insight-top">
          17 Actions
        </span>
        <span class="insight-bottom">
          3 mins ago
        </span>
      </div>
    </div> -->
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
  flex-flow: row;
  align-items: center;

  padding-left: 1rem;
  font-size: 0.875rem;
  font-weight: bold;
  line-height: 1.14;
  color: $main-font-gray;
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
</style>
