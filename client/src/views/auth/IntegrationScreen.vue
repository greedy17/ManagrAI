<template>
  <div class="integrations">
    <h2 class="title">Connect your apps to Managr</h2>
    <p style="font-weight: bold; margin-top: -0.5rem; color: #5d5e5e">
      Managr utilizes a secure oAuth connection
    </p>
    <div v-if="user.isAdmin">
      <PulseLoadingSpinnerButton
        v-if="hasSalesforceIntegration && hasSlackIntegration"
        @click="goToSlackFormBuilder"
        class="slack-button"
        text="Map your CRM Fields"
        :loading="false"
      ></PulseLoadingSpinnerButton>
      <PulseLoadingSpinnerButton
        v-else
        class="disabled-button"
        text="Map your CRM Fields"
        :loading="false"
      ></PulseLoadingSpinnerButton>
    </div>
    <div v-else>
      <PulseLoadingSpinnerButton
        v-if="hasSalesforceIntegration && hasSlackIntegration"
        @click="goToSlackFormBuilder"
        class="slack-button"
        text="Activate Workflow Automations"
        :loading="false"
      ></PulseLoadingSpinnerButton>
      <PulseLoadingSpinnerButton
        v-else
        class="disabled-button"
        text="Activate Workflow Automations"
        :loading="false"
      ></PulseLoadingSpinnerButton>
    </div>

    <div class="integrations__cards">
      <div class="card">
        <div class="required__header">
          <div class="card__header">
            <img class="card-img" src="@/assets/images/salesforce.png" />
            <h2 class="card__title">Salesforce</h2>
          </div>
          <p v-if="!hasSalesforceIntegration" class="card__required">REQUIRED</p>
        </div>

        <div>
          <p class="card-text">Sync Accounts, Opportunities, & Contacts</p>
        </div>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="!hasSalesforceIntegration"
            @click="onGetAuthLink('SALESFORCE')"
            class="orange_button"
            style="margin-left: 0.5rem"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
            >Connect</PulseLoadingSpinnerButton
          >
          <img
            src="@/assets/images/unplug.png"
            :loading="generatingToken && selectedIntegration == 'SALESFORCE'"
            @click="onRevoke('SALESFORCE')"
            v-else
            style="height: 2rem; cursor: pointer"
          />
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img class="card-img card-img__radius" src="@/assets/images/zoom.png" />
          <h2 class="card__title">Zoom</h2>
        </div>

        <p class="card-text">Activates the meeting workflow automation.</p>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="!hasZoomIntegration"
            :disabled="hasZoomIntegration"
            @click="onGetAuthLink('ZOOM')"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'ZOOM'"
          ></PulseLoadingSpinnerButton>
          <div style="display: flex; justify-content: center" v-else>
            <img
              src="@/assets/images/unplug.png"
              :loading="generatingToken && selectedIntegration == 'ZOOM'"
              @click="onRevoke('ZOOM')"
              style="height: 2rem; cursor: pointer"
            />
            <img
              src="@/assets/images/refresh.png"
              :loading="generatingToken && selectedIntegration == 'ZOOM'"
              @click="onGetAuthLink('ZOOM')"
              style="height: 2rem; cursor: pointer"
            />
          </div>
        </div>
      </div>

      <div class="card">
        <div class="required__header">
          <div class="card__header">
            <img style="height: 3rem" src="@/assets/images/slackLogo.png" />
            <h2 class="card__title">Slack</h2>
          </div>
          <p
            v-if="
              (!orgHasSlackIntegration && userCanIntegrateSlack) ||
              (orgHasSlackIntegration && !hasSlackIntegration)
            "
            class="card__required"
          >
            REQUIRED
          </p>
        </div>

        <p class="card-text">Interact with Managr through Slack</p>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="
              (!orgHasSlackIntegration && userCanIntegrateSlack) ||
              (orgHasSlackIntegration && !hasSlackIntegration)
            "
            :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
            @click="onIntegrateSlack"
            class="orange_button"
            :text="slackButtonMessage"
            :loading="generatingToken && selectedIntegration == 'SLACK'"
          ></PulseLoadingSpinnerButton>
          <div v-else-if="hasSlackIntegration && orgHasSlackIntegration">
            <img
              src="@/assets/images/unplug.png"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
              @click="onRevoke('SLACK')"
              style="height: 2rem; cursor: pointer"
            />
            <img
              src="@/assets/images/refresh.png"
              v-if="userCanIntegrateSlack"
              @click="onRefreshSlack"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
              style="height: 2rem; cursor: pointer"
            />
            <!-- <PulseLoadingSpinnerButton
              v-if="userCanIntegrateSlack"
              @click="onRefreshSlack"
              class="orange__button"
              text="Refresh"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
            ></PulseLoadingSpinnerButton> -->
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img
            class="card-img"
            src="@/assets/images/gmailCal.png"
            style="margin-right: 1rem; height: 2.5rem; width: 2.5rem"
          />
          <img class="card-img" src="@/assets/images/outlookMail.png" style="height: 3rem" />
          <h2 class="card__title">Calendar</h2>
        </div>

        <p class="card-text">Accesses your upcoming meetings + attendees</p>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="!hasNylasIntegration"
            @click="onGetAuthLink('NYLAS')"
            style="margin-left: 1rem"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
          ></PulseLoadingSpinnerButton>
          <img
            v-else
            src="@/assets/images/unplug.png"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
            @click="onRevoke('NYLAS')"
            style="height: 2rem; cursor: pointer"
          />
        </div>
        <!-- <div style="margin-bottom: 0.5rem; width: 15rem">
          <GoogleButton
            @click="onGetAuthLink('NYLAS')"
            :loading="generatingToken && selectedIntegration == 'NYLAS'"
            v-if="!hasNylasIntegration"
          />
        </div> -->
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 1.5rem" src="@/assets/images/salesloft.svg" />
        </div>
        <p class="card-text">Add Contacts to cadences</p>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="!hasSalesloftIntegration && user.isAdmin"
            :disabled="hasSalesloftIntegration"
            @click="onGetAuthLink('SALESLOFT')"
            style="margin-left: 1rem; cursor: pointer"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
          ></PulseLoadingSpinnerButton>
          <div v-else-if="hasSalesloftIntegration && user.isAdmin">
            <img
              src="@/assets/images/unplug.png"
              :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
              @click="onRevoke('SALESLOFT')"
              style="height: 2rem; cursor: pointer"
            />
            <!-- <img
              src="@/assets/images/refresh.png"
              :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
              style="height: 2rem; cursor: pointer"
            /> -->
          </div>
          <p v-else-if="hasSalesloftIntegration && !user.isAdmin">Salesloft is connected!</p>
          <p v-else>Contact your organization admin to add Salesloft</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="100"
            height="35"
            viewBox="0 0 86 30"
            preserveAspectRatio="xMinYMid meet"
          >
            <g fill="none">
              <path
                fill="#8039E9"
                d="M27.0284333,12.8254391 L18.8930861,12.8254391 C18.4282091,12.8254391 18.0740172,13.3013846 18.2400447,13.7441246 L20.1991691,18.8134974 C20.2877171,19.0348674 20.1106211,19.2783744 19.8671141,19.2673059 L17.3656332,19.1123469 C17.2549482,19.1012784 17.1442632,19.1566209 17.0778522,19.2562374 L15.1297963,22.0122937 C15.0301798,22.1672527 14.8198783,22.2225952 14.6538508,22.1119102 L11.7760409,20.1527858 C11.6653559,20.0753063 11.5103969,20.0753063 11.3997119,20.1527858 L7.41505211,22.8534997 C7.16047663,23.0305957 6.81735314,22.7870887 6.90590114,22.4882392 L8.01275109,18.5146479 C8.05702509,18.3486204 7.97954559,18.1825929 7.8135181,18.1161819 L5.69943469,17.2528389 C5.4891332,17.1642909 5.4227222,16.9097155 5.56661269,16.7326195 L7.43718911,14.4303716 C7.52573711,14.3196866 7.53680561,14.1536591 7.44825761,14.0319056 L5.87653068,11.7628632 C5.73264019,11.5525617 5.86546218,11.2647807 6.13110617,11.2426437 L8.56617607,11.0544792 C8.74327206,11.0434107 8.88716255,10.8884517 8.87609405,10.7002872 L8.68792956,7.29118936 C8.67686106,7.04768237 8.92036805,6.87058638 9.15280654,6.95913438 L12.1745069,8.20987482 C12.3073289,8.26521732 12.4622879,8.23201182 12.5508359,8.12132683 L14.6317138,5.79694193 C14.7977413,5.60877743 15.0965908,5.66411993 15.1962073,5.88548992 L16.4469477,9.10642328 C16.6129752,9.50488927 17.1110577,9.64877976 17.4652497,9.38313577 L22.3575265,5.74159943 C22.9109515,5.33206494 22.5567595,4.44658498 21.8705125,4.54620148 L18.6495791,4.97787296 C18.4946201,5 18.3507297,4.91146196 18.2953872,4.76757147 L16.6019067,0.417651154 C16.4137422,-0.036157327 15.8271118,-0.146842322 15.4950568,0.218418162 L11.8092464,4.21414649 C11.7096299,4.31376299 11.5657394,4.34696849 11.4329174,4.29162599 L6.58491465,2.24395358 C6.15324317,2.06685758 5.67729769,2.36570707 5.65516069,2.84165255 L5.4780647,7.84461434 C5.4669962,8.02171033 5.3341742,8.15453232 5.16814671,8.16560082 L0.740746899,8.45338181 C0.220527421,8.48658731 -0.0561850675,9.07321779 0.23159592,9.49382077 L3.1758168,13.8326726 C3.26436479,13.9544261 3.25329629,14.1204536 3.1536798,14.2422071 L0.165184923,17.6734419 C-0.133664564,18.0165654 -0.0119110694,18.5478534 0.408691913,18.7249494 L3.83992677,20.2081283 C3.99488576,20.2745393 4.07236526,20.4405668 4.02809126,20.5955258 L1.83652835,29.1625444 C1.68156936,29.7713119 2.36781633,30.2361889 2.87696731,29.8709284 L11.111931,23.9603497 C11.222616,23.8828702 11.3775749,23.8718017 11.4993284,23.9603497 L15.2515498,26.5946525 C15.5614678,26.8160225 15.9820708,26.7274745 16.1923722,26.4175565 L18.5388941,22.8202942 C18.6053051,22.7096092 18.7381271,22.6542667 18.8598806,22.6764037 L24.4716099,23.3515822 C24.9254184,23.4179932 25.3792269,23.0416642 25.2131994,22.6210612 L22.877746,16.5776605 C22.811335,16.411633 22.877746,16.234537 23.0769789,16.1349205 L27.3383513,14.1204536 C27.9692557,13.7994671 27.7478858,12.8254391 27.0284333,12.8254391 Z"
              ></path>
              <path
                fill="#3E0075"
                d="M85.3926313,12.8365076 L79.0725181,12.8365076 C78.9507646,12.8365076 78.8400796,12.9361241 78.8400796,13.0689461 L78.8400796,15.8692765 C78.8400796,15.99103 78.9396961,16.101715 79.0725181,16.101715 L81.773232,16.101715 C81.9060539,16.101715 82.0056704,16.2013315 82.0056704,16.3341535 C81.9835334,17.7730584 81.684684,20.3630873 79.0725181,20.3630873 C76.9362977,20.3630873 76.0840232,17.7841269 76.0840232,14.7624265 C76.0840232,11.1762327 76.9695032,8.96253279 78.9507646,8.96253279 C80.3896695,8.96253279 80.865615,10.1800677 80.998437,10.6338762 C81.0316425,10.7334927 81.1201905,10.7999037 81.219807,10.7999037 L84.5071513,10.7999037 C84.6399733,10.7999037 84.7506583,10.6892187 84.7395898,10.5563967 C84.6067678,8.7632998 83.0682464,5.61984593 79.0171756,5.61984593 C76.1836397,5.61984593 73.5271998,7.34653186 72.6749253,11.6079042 L72.6749253,6.10685991 C72.6749253,6.04044891 72.6195828,5.99617492 72.5642403,5.99617492 L69.0887315,5.99617492 C69.0223205,5.99617492 68.9780465,6.05151741 68.9780465,6.10685991 L68.9780465,15.9135505 C68.9780465,16.035304 68.812019,16.0685095 68.7566765,15.9578245 L64.1964547,6.05151741 C64.1743177,6.00724342 64.1411122,5.98510642 64.0968382,5.98510642 L61.0197953,5.98510642 C60.9533843,5.98510642 60.9091103,6.04044891 60.9091103,6.09579141 L60.9091103,11.5968357 C59.7690549,8.11025833 56.669875,5.60877743 52.6409412,5.60877743 C48.1471304,5.60877743 44.815512,8.7190258 44.0517856,12.8475761 L37.7538093,12.8475761 C37.6873983,12.8475761 37.6431243,12.9029186 37.6431243,12.9582611 L37.6431243,15.99103 C37.6431243,16.057441 37.6984668,16.101715 37.7538093,16.101715 L40.6869617,16.101715 C40.7533727,16.101715 40.7976467,16.1570575 40.7976467,16.2124 C40.7865782,17.6180994 40.5430712,20.3520188 37.8534258,20.3520188 C35.7172054,20.3520188 34.8649309,17.7730584 34.8649309,14.751358 C34.8649309,11.1651642 35.7504109,8.95146429 37.7316723,8.95146429 C39.2591253,8.95146429 39.7018652,10.3350267 39.8014817,10.7002872 C39.8125502,10.7556297 39.8568242,10.7888352 39.9121667,10.7888352 L43.4098126,10.7888352 C43.4762236,10.7888352 43.5315661,10.7334927 43.5204976,10.6670817 C43.4540866,8.89612179 41.9377021,5.60877743 37.7870148,5.60877743 C34.3447115,5.60877743 31.1680521,8.15453232 31.1680521,14.7181525 C31.1680521,19.2341004 32.939012,23.6947057 37.8423573,23.6947057 C41.4728252,23.6947057 43.7972101,20.8833068 44.306361,17.5074144 C45.4021425,21.1046768 48.5345279,23.6947057 52.6409412,23.6947057 C56.603464,23.6947057 59.7579864,21.1821563 60.9091103,17.6734419 L60.9091103,23.2298287 C60.9091103,23.2962397 60.9644528,23.3405137 61.0197953,23.3405137 L64.4953042,23.3405137 C64.5617152,23.3405137 64.6059892,23.2851712 64.6059892,23.2298287 L64.6059892,13.5780971 C64.6059892,13.4563436 64.7720167,13.4231381 64.8273592,13.5338231 L69.387581,23.2851712 C69.409718,23.3294452 69.4429235,23.3515822 69.4871975,23.3515822 L72.5642403,23.3515822 C72.6306513,23.3515822 72.6749253,23.2962397 72.6749253,23.2408972 L72.6749253,17.7287844 C73.3501038,21.0382658 75.2649542,23.7168427 79.0614496,23.7168427 C83.2010684,23.7168427 85.6361383,20.0753063 85.6361383,16.0906465 L85.6361383,13.1021516 C85.6250698,12.9361241 85.5143848,12.8365076 85.3926313,12.8365076 Z M52.6188042,20.0753063 C49.6967203,20.0753063 47.6711849,17.8284009 47.6711849,14.6517415 C47.6711849,11.4750822 49.6967203,9.22817678 52.6188042,9.22817678 C55.5298196,9.22817678 57.5664235,11.4750822 57.5664235,14.6517415 C57.5664235,17.8284009 55.5298196,20.0753063 52.6188042,20.0753063 Z"
              ></path>
            </g>
          </svg>
        </div>
        <p class="card-text">Access call recordings and insights</p>
        <div class="card__body">
          <PulseLoadingSpinnerButton
            v-if="!hasGongIntegration && user.isAdmin"
            :disabled="hasGongIntegration"
            @click="onGetAuthLink('GONG')"
            style="margin-left: 1rem; cursor: pointer"
            class="orange_button"
            text="Connect"
            :loading="generatingToken && selectedIntegration == 'GONG'"
          ></PulseLoadingSpinnerButton>
          <div v-else-if="hasGongIntegration && user.isAdmin">
            <img
              src="@/assets/images/unplug.png"
              :loading="generatingToken && selectedIntegration == 'GONG'"
              @click="onRevoke('GONG')"
              style="height: 2rem; cursor: pointer"
            />
          </div>
          <p v-else-if="hasGongIntegration && !user.isAdmin">Gong is connected!</p>
          <p v-else>Contact your organization admin to add Gong</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="width: 4rem" src="@/assets/images/hubspott.png" />
          <h2 class="card__title">Hubspot</h2>
        </div>
        <p class="card-text">Sync Companies, Deals, and Contacts</p>
        <div class="card__body">
          <p style="color: #beb5cc">Coming Soon</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 3.5rem" src="@/assets/images/teamsLogo.png" />
          <h2 class="card__title">Teams</h2>
        </div>
        <p class="card-text">Interact with Managr through Teams</p>
        <div class="card__body">
          <p style="color: #beb5cc">Coming Soon</p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <img style="height: 3rem" src="@/assets/images/googleDrive.png" />
          <h2 class="card__title">Google Drive</h2>
        </div>
        <p class="card-text">Enable battlecards and playbooks</p>
        <div class="card__body">
          <p style="color: #beb5cc">Coming Soon</p>
        </div>
      </div>
    </div>

    <img class="lock" src="@/assets/images/blackLock.png" />
    <p class="privacy"><strong>SOC2</strong> certified, and <strong>GDPR</strong> compliant</p>
    <!-- <p>
      <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a>
      |
      <a href="https://managr.ai/documentation" target="_blank">Documentation</a>
      |
      <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>
    </p> -->
  </div>
</template>

<script>
/**
 * Page that shows a grid of all possible integrations and 'Connect' buttons.
 */

import SlackOAuth from '@/services/slack'
import ZoomAccount from '@/services/zoom/account/'
import Nylas from '@/services/nylas'
import Salesforce from '@/services/salesforce'
import SalesloftAccount from '@/services/salesloft'
import GongAccount from '@/services/gong'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import GoogleButton from '@/components/GoogleButton'

export default {
  name: 'Integrations',
  components: { PulseLoadingSpinnerButton, GoogleButton },
  data() {
    return {
      generatingToken: false,
      authLink: null,
      selectedIntegration: null,
    }
  },
  methods: {
    goToSlackFormBuilder() {
      this.$router.push({ name: 'Configure' })
    },
    goToSmartAlerts() {
      this.$router.push({ name: 'ListTemplates' })
    },
    async onGetAuthLink(integration) {
      this.generatingToken = true
      this.selectedIntegration = integration
      const modelClass = this.selectedIntegrationSwitcher
      try {
        const res = await modelClass.api.getAuthLink()
        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        this.generatingToken = false
      }
    },
    async onRevoke(integration) {
      this.generatingToken = true
      this.selectedIntegration = integration
      try {
        await this.selectedIntegrationSwitcher.api.revoke()
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
      }
    },
    async onIntegrateSlack() {
      const confirmation = confirm(
        'Integrating Managr to your slack workspace will request access to a channel (you can choose a new one or an existing one) we will post a message letting the members of that channel know they can now integrate their Slack accounts',
      )
      if (!confirmation) {
        return
      }
      this.generatingToken = true
      if (!this.orgHasSlackIntegration) {
        if (this.userCanIntegrateSlack) {
          try {
            let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.WORKSPACE)
            if (res.link) {
              window.location.href = res.link
            }
          } finally {
            this.generatingToken = false
          }
        }
      } else {
        if (!this.hasSlackIntegration) {
          try {
            let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.USER)
            if (res.link) {
              window.location.href = res.link
            }
          } catch (e) {
          } finally {
            this.generatingToken = false
          }
        }
      }
    },
    async onRefreshSlack() {
      const confirmation = confirm('This will refresh the access token for the workspace')
      if (!confirmation) {
        return
      }
      this.generatingToken = true
      if (this.orgHasSlackIntegration && this.userCanIntegrateSlack) {
        try {
          let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.WORKSPACE)
          if (res.link) {
            window.location.href = res.link
          }
        } finally {
          this.generatingToken = false
        }
      }
    },
  },
  async created() {
    // if there is a code assume an integration has begun
    if (this.$route.query.code) {
      this.generatingToken = true
      this.selectedIntegration = this.$route.query.state // state is the current integration name

      try {
        const modelClass = this.selectedIntegrationSwitcher
        if (this.selectedIntegration == 'SALESLOFT') {
          await modelClass.api.authenticate(
            this.$route.query.code,
            this.$route.query.context,
            this.$route.query.scope,
          )
        } else if (this.selectedIntegration != 'SLACK' && this.selectedIntegration != 'SALESLOFT') {
          await modelClass.api.authenticate(this.$route.query.code)
        } else {
          // auto sends a channel message, will also send a private dm
          await SlackOAuth.api.generateAccessToken(this.$route.query.code)
        }
      } catch (e) {
        let { response } = e
        if (response && response.status >= 400 && response.status < 500 && response.status != 401) {
          let { data } = response
          if (data.timezone) {
            this.$Alert.alert({
              type: 'error',
              message:
                '<h3>We could not retrieve your timezone from zoom, to fix this please login to the zoom.us portal through a browser and return to managr to reintegrate</h3>',
            })
          }
        }
      } finally {
        await this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.selectedIntegration = null
        this.$router.replace({
          name: 'Integrations',
          params: {},
        })
      }
    }
  },
  computed: {
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
    hasGongIntegration() {
      return !!this.$store.state.user.gongAccount && this.$store.state.user.hasGongIntegration
    },
    hasSalesloftIntegration() {
      return (
        !!this.$store.state.user.salesloftAccount && this.$store.state.user.hasSalesloftIntegration
      )
    },
    orgHasSlackIntegration() {
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      return this.$store.state.user.isAdmin
    },

    selectedIntegrationSwitcher() {
      switch (this.selectedIntegration) {
        case 'SALESFORCE':
          return Salesforce
        case 'ZOOM':
          return ZoomAccount
        case 'NYLAS':
          return Nylas
        case 'SLACK':
          return SlackOAuth
        case 'SALESLOFT':
          return SalesloftAccount
        case 'GONG':
          return GongAccount
        default:
          return null
      }
    },
    user() {
      return this.$store.state.user
    },
    slackButtonMessage() {
      if (!this.orgHasSlackIntegration && this.userCanIntegrateSlack) {
        return 'Connect'
      } else if (this.orgHasSlackIntegration && !this.hasSlackIntegration) {
        return 'Connect'
      } else {
        return 'N/A'
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.integrations {
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}

.card {
  background-color: $panther;
  padding: 2rem;
  border: none;
  max-height: 30vh;
  margin-right: 1rem;
  margin-bottom: 2rem;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 4px 7px black;
  @media only screen and (min-width: 768px) {
    flex: 1 0 24%;
    min-width: 21rem;
    max-width: 30rem;
  }

  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    min-height: 4rem;
  }

  &__title {
    margin: 0 0 0 1rem;
  }

  &__body {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
  }
  &__required {
    color: $panther-orange;
    font-size: 0.8rem;
    font-weight: bold;
    padding: 0.5rem;
    border-radius: 0.5rem;
    text-shadow: 0.75px 0.3px 0.2px white;
  }
}

.required__header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.card-img {
  width: 3rem;
}

.card-text {
  font-size: 14px;
  font-weight: bold;
  color: $panther-silver;
  text-align: center;
}

.slack-button {
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  margin: 0rem 0 1rem 0;
  font-size: 1.05rem;
  font-weight: bold;
  color: white;
  background-color: $dark-green;
  border: none;
  cursor: pointer;
}
.disabled-button {
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  margin: 0rem 0 1rem 0;
  font-size: 1.05rem;
  font-weight: bold;
  border: none;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
}
.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}

.privacy {
  font-family: #{$bold-font-family};
  color: black;
  font-size: 16px;
}

.lock {
  height: 2rem;
}
.note {
  font: lato-bold;
  font-size: 13px;
  font-weight: 900;
  color: $mid-gray;
  margin-top: -2.5rem;
}
.bold {
  font: lato-bold;
  font-weight: 2rem;
  color: $light-gray-blue;
}
.title {
  font-weight: bold;
  color: black;
}
a {
  text-decoration: none;
  color: $grape;
  font-weight: bold;
}
.alertButton__ {
  height: 2.5rem;
  width: 19rem;
  margin: 0rem 0 2rem 0;
  color: white;
  background-color: $dark-green;
  border: none;
  font-weight: bold;
  font-size: 14px;
  border-radius: 0.25rem;
  cursor: pointer;
}

.end {
  width: 6rem;
  align-self: flex-end;
  color: $panther-silver;
  background: transparent;
  border: none;
}

.orange_button {
  color: white;
  background-color: $dark-green;
  border-radius: 0.5rem;
  padding: 0.5rem 1.5rem;
  font-weight: bold;
  font-size: 1rem;
  border: none;
  transition: all 0.25s;
  cursor: pointer;
}

.orange_button:hover {
  transform: scale(1.05);
}

.connected {
  margin-left: 2rem;
  color: $dark-green;
  font-size: 1.1rem;
  font-weight: bold;
  text-shadow: 0 0 20px $dark-green;
}

.revoke {
  color: $panther-silver;
  background-color: transparent;
  width: 7vw;
  border-radius: 0.25rem;
  padding: 0.25rem;
  margin-left: 1rem;
  font-weight: bold;
  font-size: 14px;
  border: 2px solid $panther-silver;
  cursor: pointer;
}
.revoke__ {
  color: $panther-silver;
  background-color: transparent;
  width: 5vw;
  border-radius: 0.25rem;
  padding: 0.25rem;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  font-weight: bold;
  font-size: 14px;
  border: 2px solid $panther-silver;
  cursor: pointer;
}
.revoke,
.revoke__:hover {
  filter: brightness(0.85);
}
</style>

￼

