<template>
  <div class="notifications">
    <div class="notifications__header__container">
      <div class="notifications__header__title">Customize your Notifications and Alerts</div>
      <div class="notifications__header__container__text">
        <div class="notifications__header__text">Coming Soon...</div>
        <div class="notifications__header__text">Invite and Customize your Team</div>
      </div>
    </div>
    <div class="notifications__body__container">
      <div class="notifications__body">
        <div class="notifications__body__section">
          <div class="notifications__body__section__left">
            <div class="notifications__body__section__row">
              <div class="notifications__body__section__left__title">Automated Assistance</div>
              <div class="notifications__body__section__left__subtitle">Time</div>
            </div>
            <div class="notifications__body__section__left__item__container">
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div class="notifications__body__section__left__item__title">Day Prep</div>
                  <div class="notifications__body__section__left__item__option">
                    <div class="notifications__body__section__left__item__option__text">8AM EST</div>
                  </div>
                </div>
              </div>
              <div
                class="notifications__body__section__left__item__text"
              >Upcoming meetings and tasks for the day</div>
            </div>
          </div>
        </div>
        <div class="notifications__body__section">
          <div class="notifications__body__section__left">
            <div class="notifications__body__section__left__item__container">
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div class="notifications__body__section__left__item__title">Meeting Prep</div>
                  <div class="notifications__body__section__left__item__option">
                    <div
                      class="notifications__body__section__left__item__option__text"
                    >30 min before</div>
                  </div>
                </div>
              </div>
              <div
                class="notifications__body__section__left__item__text"
              >Attendee info, notes, and insights about upcoming meeting</div>
            </div>
          </div>
        </div>
        <div class="notifications__body__section">
          <div class="notifications__body__section__left">
            <div class="notifications__body__section__row">
              <div class="notifications__body__section__left__title">Deal Slipping Alerts</div>
              <div class="notifications__body__section__left__subtitle">Days</div>
            </div>
            <div
              class="notifications__body__section__left__item__text"
            >Alerts you when deals are becoming stale</div>
            <div class="notifications__body__section__left__item__container">
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Deal stuck in stage for X days</div>
                  <div class="notifications__body__section__left__item__option">
                    <div class="notifications__body__section__left__item__option__text">7 days</div>
                  </div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Deal has no activity for X days</div>
                  <div class="notifications__body__section__left__item__option">
                    <div class="notifications__body__section__left__item__option__text">14 days</div>
                  </div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Expected close date has passed for X days</div>
                  <div class="notifications__body__section__left__item__option">
                    <div class="notifications__body__section__left__item__option__text">7 days</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="notifications__body__section" v-if="isAdmin" style="margin-top: 2rem;">
          <div class="notifications__body__section__left">
            <div class="notifications__body__section__row">
              <div class="notifications__body__section__left__title">Insights and Reporting</div>
            </div>
            <div class="notifications__body__section__left__item__text">Meeting Alert Conditions</div>
            <div class="notifications__body__section__left__item__container">
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Alert me when a meeting has moved to Commit</div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Alert me when a meeting went "Great"</div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Alert me about a meeting from an opportuinity that is expected to close in the current week</div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Only alert me when all three of the above are true</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="notifications__body__section" style="margin-top: 2rem;" v-if="isAdmin">
          <div class="notifications__body__section__left">
            <div class="notifications__body__section__row">
              <div class="notifications__body__section__left__title">Additional Reporting Tools</div>
              <div class="notifications__body__section__left__subtitle">Time</div>
            </div>
            <div class="notifications__body__section__left__item__container">
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div
                    class="notifications__body__section__left__item__title"
                  >Send Story Report from Closed Deal</div>
                </div>
              </div>
              <div class="notifications__body__section__row">
                <div class="notifications__body__section__left__item__header">
                  <CheckBox :checked="toggle" />
                  <div class="notifications__body__section__left__item__title">Send Weekly Recaps</div>
                  <div class="notifications__body__section__left__item__option">
                    <div class="notifications__body__section__left__item__option__text">6PM EST</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CheckBox from '@/components/CheckBoxUpdated'
export default {
  name: 'Notifications',
  components: {
    CheckBox,
  },
  data() {
    return {
      isAdmin: null,
      toggle: true,
    }
  },
  created() {
    const user = this.$store.state.user
    this.isAdmin = user.isAdmin
  },
}
</script>

<style lang="scss">
@import '@/styles/variables';

.notifications {
  &__header {
    &__container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 3rem;
      font-size: 1.25rem;

      &__text {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 2rem 0;
        font-size: 14px;
      }
    }
    &__title {
      font-family: #{$bold-font-family};
    }
  }

  &__body {
    width: 60%;

    margin: 45px 108px 1px 35px;
    padding: 25px 17px 32px 39.6px;
    border-radius: 5px;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    border: solid 2px #dcdddf;
    background-color: #ffffff;
    left: 13rem;
    top: -6rem;

    &__container {
      display: flex;
      justify-content: center;
    }

    &__section {
      display: flex;
      flex-direction: row;
      &__row {
        display: flex;
        width: 100%;
      }
      &__left {
        width: 100%;

        &__title {
          font-weight: 900;
          width: 80%;
        }
        &__subtitle {
          font-weight: 900;
          font-family: #{$bold-font-family};
          font-size: 14px;
          width: 20%;
          display: flex;
          justify-content: center;
        }
        &__item {
          &__container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-top: 0.5rem;
          }
          &__header {
            display: flex;
            align-items: center;
            width: 100%;
          }

          &__title {
            font-family: #{$bold-font-family};
            font-size: 0.75rem;
            margin-left: 0.5rem;
            width: 80%;
          }
          &__option {
            display: flex;
            justify-content: center;
            font-size: 0.75rem;

            width: 20%;

            &__text {
              border: 1px solid #eaebed;
              padding: 0 0.5rem;
            }
          }
          &__text {
            font-size: 0.75rem;
            margin: 0.5rem 0 1rem 0.5rem;
          }
        }
      }
    }
  }
}
</style>

