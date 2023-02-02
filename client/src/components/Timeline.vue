<template>
  <div style="margin-top: 1rem; margin-left: -95%">
    <div class="timeline">
      <div class="timeline-container right row">
        <img
          class="timeline-pic gold-filter"
          src="@/assets/images/doubleCheck.svg"
          height="14px"
          alt=""
        />
        <div class="content">
          <p class="light-gray-text">
            <span class="bold">Stage</span> changed from <s class="gray-section">Negotiation</s> to
            <span class="green-section">Closed Won</span>
          </p>
          <ul>
            <li class="light-gray-text">6 additional fields were updated</li>
          </ul>
        </div>

        <small class="light-gray-text">Today</small>
      </div>
      <div class="timeline-container right row">
        <img class="timeline-pic" src="@/assets/images/trendingUp.svg" height="14px" alt="" />
        <div class="content">
          <p class="light-gray-text">
            <span class="bold">Amount</span> changed from <s class="gray-section">$25,000</s> to
            <span class="green-section">$29,000</span>
          </p>
        </div>

        <small class="light-gray-text">Yesterday</small>
      </div>
      <div class="timeline-container right row">
        <img class="timeline-pic" src="@/assets/images/person.svg" height="14px" alt="" />
        <div class="content">
          <p class="light-gray-text">
            <span class="bold">Meeting</span> Discovery call with John just ended.
          </p>
          <ul>
            <li class="light-gray-text">1 attendee joined the meeting</li>
          </ul>
        </div>
        <small class="light-gray-text">8 days ago</small>
      </div>
      <div class="timeline-container right row">
        <img class="timeline-pic" src="@/assets/images/calendar.svg" height="14px" alt="" />
        <div class="content">
          <p class="light-gray-text">
            <span class="bold">Close Date</span> pushed from <s>12/12/22</s> to 12/17/22
          </p>
        </div>
        <small class="light-gray-text">12/10/22</small>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.light-gray-text {
  color: $light-gray-blue;
  font-size: 14px;
}

.bold {
  font-weight: bold;
  font-size: 15px;
  color: $base-gray;
}

::v-deep .gb-vue-timeline-update__title {
  font-size: 16px !important;
}

::v-deep .gb-vue-timeline-update__ago {
  font-size: 12px !important;
  //   font: $base-font-family !important;
  //   font-family: $base-font-family !important;
}

::v-deep .gb-vue-timeline-update__description {
  font-size: 16px !important;
  letter-spacing: 0.75px !important;
  color: $light-gray-blue !important;
}

/* The actual timeline (the vertical ruler) */
.timeline {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
}

/* The actual timeline (the vertical ruler) */
.timeline::after {
  content: '';
  position: absolute;
  width: 3px;
  background-color: $soft-gray;
  top: 0;
  bottom: 0;
  left: 50%;
  margin-left: -3px;
}

.timeline-container {
  padding: 10px 40px;
  position: relative;
  background-color: inherit;
  width: 50%;
}

.timeline-pic {
  padding: 0;
  position: absolute;
  z-index: 2;
  left: 0;
  top: 0;
  margin-top: 1.4rem;
  margin-left: -0.6rem;

  filter: invert(80%);

  //   outline: 1px solid red;
}

/* The circles on the timeline */
.timeline-container::after {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  right: -17px;
  background-color: white;
  border: 3px solid $soft-gray;
  top: 15px;
  border-radius: 50%;
  z-index: 1;
}

.right {
  left: 50%;
}

.right::after {
  left: -16px;
}

.content {
  padding: 20px 30px;
  background-color: white;
  position: relative;
  border-radius: 8px;
  //   border: 1px solid $soft-gray;
  width: 36vw;
  margin-top: -1.5rem;
  margin-left: -2rem;
}

.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  width: 50vw;
}

small {
  font-size: 12px !important;
}

.gray-section {
  letter-spacing: 0.75px;
  color: $light-gray-blue;
  background-color: $soft-gray;
  padding: 4px 6px;
  border-radius: 4px;
  font-weight: bold;
}

.green-section {
  letter-spacing: 0.75px;
  color: $dark-green;
  background-color: $white-green;
  padding: 4px 6px;
  border-radius: 4px;
  font-weight: bold;
}
.gold-filter {
  filter: invert(81%) sepia(35%) saturate(920%) hue-rotate(343deg) brightness(91%) contrast(90%);
}
</style>