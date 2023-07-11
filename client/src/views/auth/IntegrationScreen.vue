<template>
  <div class="integrations">
    <Modal
      v-if="confirmModal"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), handleConfirmCancel()
        }
      "
    >
      <form v-if="true /*hasSlack*/" class="invite-form modal-form confirm-form form-margin-small">
        <div class="header">
          <div class="flex-row-wrapper">
            <div class="flex-row">
              <img src="@/assets/images/logo.png" class="logo" alt="" />
              <h3 class="invite-form__title">Are you sure?</h3>
            </div>
            <div class="flex-row">
              <img
                @click="handleConfirmCancel"
                src="@/assets/images/close.svg"
                alt=""
                style="
                  filter: invert(30%);
                  cursor: pointer;
                  width: 20px;
                  height: 20px;
                  margin-right: 5px;
                "
              />
            </div>
          </div>
          <div class="flex-row">
            <h4 class="invite-form__subtitle">
              By clicking Confirm, you will be disconnecting
              {{ this.removeAppFormatted ? this.removeAppFormatted : 'this app' }}.
            </h4>
          </div>
        </div>
        <div class="invite-form__actions">
          <!-- <div style="width: 10vw;"></div> -->
          <div class="invite-form__inner_actions">
            <template>
              <PulseLoadingSpinnerButton
                @click="onRevoke(removeApp)"
                class="invite-button modal-button"
                style="width: 5rem; margin-right: 5%; height: 2rem"
                text="Confirm"
                :loading="pulseLoading"
                >Confirm</PulseLoadingSpinnerButton
              >
            </template>
          </div>
        </div>
      </form>
    </Modal>
    <div class="welcome">
      <!-- <img src="@/assets/images/logo.png" height="16px" alt="" /> -->
      <p class="inactive">Connect Managr to your favorite Apps</p>
    </div>

    <div class="integrations__cards">
      <div class="card" v-if="userCRM === 'SALESFORCE'">
        <div class="card__header vlb-bg" style="padding-left: 32px; padding-right: 32px">
          <img style="height: 30px; width: auto" src="@/assets/images/salesforce.png" />
        </div>

        <div class="card__body">
          <h3>
            Salesforce
            <span class="required" v-if="!hasSalesforceIntegration">
              <img src="@/assets/images/required.svg" height="14px" alt=""
            /></span>
          </h3>
          <p class="card-text">Sync Accounts, Opportunities, & Contacts</p>
          <div>
            <div>
              <div class="img-border">
                <img
                  @click="setRemoveApp('SALESFORCE')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card" v-else-if="userCRM === 'HUBSPOT'">
        <div class="card__header lo-bg">
          <img style="height: 80px" src="@/assets/images/hubspott.png" />
        </div>

        <div class="card__body">
          <h3 class="card__title">
            Hubspot
            <span class="required" v-if="!hasHubspotIntegration">
              <img src="@/assets/images/required.svg" height="14px" alt=""
            /></span>
          </h3>
          <p class="card-text">Sync Companies, Deals, and Contacts</p>
          <div>
            <div>
              <div class="img-border">
                <img
                  @click="setRemoveApp('HUBSPOT')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card" v-else>
        <div class="card__header og-bg" style="padding-left: 18px; padding-right: 18px">
          <img style="height: 30px; width: auto" src="@/assets/images/salesforce.png" />
          <img style="height: 30px" src="@/assets/images/hubspot-single-logo.svg" />
        </div>
        <div
          class="card__body"
          v-if="
            generatingToken &&
            (selectedIntegration == 'SALESFORCE' || selectedIntegration === 'HUBSPOT')
          "
        >
          <PipelineLoader />
        </div>
        <div v-else>
          <div class="card__body">
            <div style="display: flex">
              <h3 class="card__title">CRM</h3>
              <span class="required" v-if="!userCRM">
                <img src="@/assets/images/required.svg" height="14px" alt=""
              /></span>
            </div>
            <p class="card-text">Select a CRM you would like to link</p>
            <div>
              <Multiselect
                placeholder="Select CRM"
                @input="onGetAuthLink($event.value)"
                :v-model="selectedCRM"
                :options="crmList"
                openDirection="below"
                style="width: 14rem"
                selectLabel="Enter"
                track-by="value"
                label="label"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select CRM
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header lr-bg" style="padding-left: 36px; padding-right: 36px">
          <img style="height: 40px" src="@/assets/images/slackLogo.png" />
        </div>

        <div class="card__body">
          <h3>
            Slack
            <span class="required" v-if="!hasSlackIntegration">
              <img src="@/assets/images/required.svg" height="14px" alt=""
            /></span>
          </h3>
          <p class="card-text">Interact with Managr through Slack</p>
          <div>
            <PulseLoadingSpinnerButton
              v-if="!hasSlackIntegration"
              :disabled="(!orgHasSlackIntegration && !userCanIntegrateSlack) || hasSlackIntegration"
              @click="onIntegrateSlack"
              class="orange_button"
              :text="slackButtonMessage"
              :loading="generatingToken && selectedIntegration == 'SLACK'"
            ></PulseLoadingSpinnerButton>

            <div class="row" v-else>
              <div class="img-border">
                <img
                  @click="setRemoveApp('SLACK')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
              <div class="img-border">
                <img
                  @click="onGetAuthLink('SLACK')"
                  src="@/assets/images/refresh.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header lbp-bg">
          <img src="@/assets/images/gmailCal.png" style="margin-right: 16px; height: 32px" />
          <img src="@/assets/images/outlookMail.png" style="height: 32px" />
          <!-- <img class="filter-dot" src="@/assets/images/dot.svg" v-if="hasNylasIntegration" /> -->
        </div>

        <div class="card__body">
          <h3>Calendar</h3>
          <p class="card-text">Accesses your upcoming meetings</p>
          <div>
            <PulseLoadingSpinnerButton
              v-if="!hasNylasIntegration"
              @click="onGetAuthLink('NYLAS')"
              class="orange_button"
              text="Connect"
              :loading="generatingToken && selectedIntegration == 'NYLAS'"
            ></PulseLoadingSpinnerButton>
            <div v-else>
              <div class="img-border">
                <img
                  @click="setRemoveApp('NYLAS')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header vlb-bg" style="padding-left: 34px; padding-right: 34px">
          <img style="height: 40px" src="@/assets/images/zoom.png" />
          <!-- <img class="filter-dot" src="@/assets/images/dot.svg" v-if="hasZoomIntegration" /> -->
        </div>

        <div class="card__body">
          <div class="space-between">
            <h3 class="card__title">Zoom</h3>
            <!-- <img
                class="gold-filter shimmer"
                src="@/assets/images/premium.svg"
                height="24"
                alt=""
              /> -->
          </div>

          <p class="card-text">Activates meeting workflow automations.</p>
          <div>
            <PulseLoadingSpinnerButton
              v-if="!hasZoomIntegration"
              :disabled="hasZoomIntegration"
              @click="onGetAuthLink('ZOOM')"
              class="orange_button"
              text="Connect"
              :loading="generatingToken && selectedIntegration == 'ZOOM'"
            ></PulseLoadingSpinnerButton>

            <div class="row" v-else>
              <div class="img-border">
                <img
                  @click="setRemoveApp('ZOOM')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
              <div class="img-border">
                <img
                  @click="onGetAuthLink('ZOOM')"
                  src="@/assets/images/refresh.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
          <!-- <div v-else class="side-wrapper">
            <label class="side-icon side-workflow" style="">
              <span class="side-tooltip">Upgrade your plan</span>
              <img class="shimmer" src="@/assets/images/lock.svg" height="18" alt="" />
            </label>
          </div> -->
        </div>
      </div>

      <div class="card">
        <div class="card__header lg-bg">
          <img class="filter-loft" style="height: 18px" src="@/assets/images/salesloft.svg" />
          <!-- <img class="filter-dot" src="@/assets/images/dot.svg" v-if="hasSalesloftIntegration" /> -->
        </div>

        <div class="card__body">
          <h3>Salesloft</h3>
          <p class="card-text">Add Contacts to Cadences</p>
          <div v-if="isPaid">
            <PulseLoadingSpinnerButton
              v-if="!hasSalesloftIntegration"
              :disabled="hasSalesloftIntegration"
              @click="onGetAuthLink('SALESLOFT')"
              class="orange_button"
              text="Connect"
              :loading="generatingToken && selectedIntegration == 'SALESLOFT'"
            ></PulseLoadingSpinnerButton>
            <div v-else-if="hasSalesloftIntegration">
              <div class="img-border">
                <img
                  @click="setRemoveApp('SALESLOFT')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
          <div v-else class="side-wrapper">
            <label class="side-icon side-workflow" style="">
              <span class="side-tooltip">Upgrade your plan</span>
              <img class="shimmer" src="@/assets/images/lock.svg" height="18" alt="" />
            </label>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header vlp-bg">
          <img style="height: 15px" src="@/assets/images/outreach.webp" />
        </div>

        <div class="card__body">
          <h3>Outreach</h3>

          <p class="card-text">Add Contacts to Sequences</p>

          <div v-if="true /*isPaid*/">
            <PulseLoadingSpinnerButton
              v-if="!hasOutreachIntegration"
              :disabled="hasOutreachIntegration"
              @click="onGetAuthLink('OUTREACH')"
              class="orange_button"
              text="Connect"
              :loading="generatingToken && selectedIntegration == 'OUTREACH'"
            ></PulseLoadingSpinnerButton>
            <div class="row" v-else>
              <div class="img-border">
                <img
                  @click="setRemoveApp('OUTREACH')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
              <div class="img-border">
                <img
                  @click="onGetAuthLink('OUTREACH')"
                  src="@/assets/images/refresh.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
          <div v-else class="side-wrapper">
            <label class="side-icon side-workflow" style="">
              <span class="side-tooltip">Upgrade your plan</span>
              <img class="shimmer" src="@/assets/images/lock.svg" height="18" alt="" />
            </label>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header lp-bg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="75"
            height="27"
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
          <!-- <img class="filter-dot" src="@/assets/images/dot.svg" v-if="hasGongIntegration" /> -->
        </div>

        <div class="card__body">
          <h3>Gong</h3>
          <p class="card-text">Access call recordings & insights</p>
          <div v-if="isPaid">
            <PulseLoadingSpinnerButton
              v-if="!hasGongIntegration && user.isAdmin"
              :disabled="hasGongIntegration"
              @click="onGetAuthLink('GONG')"
              class="orange_button"
              text="Connect"
              :loading="generatingToken && selectedIntegration == 'GONG'"
            ></PulseLoadingSpinnerButton>

            <div v-else>
              <div class="img-border">
                <img
                  @click="setRemoveApp('GONG')"
                  src="@/assets/images/revoke.svg"
                  height="16"
                  alt=""
                />
              </div>
            </div>
          </div>
          <div v-else class="side-wrapper">
            <label class="side-icon side-workflow" style="">
              <span class="side-tooltip">Upgrade your plan</span>
              <img class="shimmer" src="@/assets/images/lock.svg" height="18" alt="" />
            </label>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card__header lb-bg" style="padding-left: 32px; padding-right: 32px">
          <img style="height: 40px" src="@/assets/images/teamsLogo.png" />
        </div>

        <div class="card__body">
          <h3 class="card__title">Teams</h3>
          <p class="card-text">Interact with Managr through Teams</p>
          <div>
            <p style="color: #beb5cc">Coming Soon</p>
          </div>
        </div>
      </div>

      <!-- VVV THIS IS FOR CHOOSING A MESSENGER APP TO LINK TO MANAGR AT A LATER DATE VVV -->

      <!-- <div class="card">
          <div class="card__body">
            <h3 class="card__title">Messenger</h3>
            <p class="card-text">Select a Messenger you would like to link</p>
            <div>
              <Multiselect
                placeholder="Select Messenger"
                @input="onGetAuthLink($event.value)"
                :v-model="selectedMessenger"
                :options="messengerList"
                openDirection="below"
                style="width: 21rem;"
                selectLabel="Enter"
                track-by="value"
                label="label"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Messenger
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div> -->
    </div>
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
import Hubspot from '@/services/hubspot'
import SalesloftAccount from '@/services/salesloft'
import GongAccount from '@/services/gong'
import OutreachAccount from '@/services/outreach'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import { CollectionManager } from '@thinknimble/tn-models'
import Modal from '@/components/InviteModal'
import Loader from '@/components/Loader'
import { decryptData } from '../../encryption'

export default {
  name: 'Integrations',
  components: {
    PulseLoadingSpinnerButton,
    CollectionManager,
    Modal,
    Loader,
    PipelineLoader: () => import(/* webpackPrefetch: true */ '@/components/PipelineLoader'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      generatingToken: false,
      crmList: [
        { label: 'Salesforce', value: 'SALESFORCE' },
        { label: 'Hubspot', value: 'HUBSPOT' },
      ],
      // messengerList: [
      //   { label: 'Slack', value: 'SLACK' },
      //   { label: 'Teams', value: 'TEAMS' },
      // ],
      removeApp: '',
      removeAppFormatted: '',
      confirmModal: false,
      pulseLoading: false,
      selectedCRM: null,
      // selectedMessenger: null,
      selectedIntegration: null,
    }
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    async onGetAuthLink(integration) {
      integration === 'NYLAS'
        ? confirm(
            'You must check all permission boxes in order for Managr to successfully connect to your calendar!',
          )
        : ''
      this.generatingToken = true
      this.selectedIntegration = integration

      let modelClass = this.selectedIntegrationSwitcher
      try {
        let res
        if (integration === 'SLACK') {
          res = this.onIntegrateSlack()
        } else {
          res = await modelClass.api.getAuthLink()
        }
        if (res.link) {
          window.location.href = res.link
        }
      } finally {
        this.generatingToken = false
      }
    },
    async onRevoke(integration) {
      this.generatingToken = true
      this.pulseLoading = true
      this.selectedIntegration = integration
      try {
        await this.selectedIntegrationSwitcher.api.revoke()
      } finally {
        this.$store.dispatch('refreshCurrentUser')
        this.generatingToken = false
        this.pulseLoading = false
        this.confirmModal = false
      }
    },
    setRemoveApp(appName) {
      if (appName) {
        this.removeApp = appName
        this.removeAppFormatted = appName[0] + appName.slice(1).toLowerCase()
        this.confirmModal = true
      }
    },
    handleConfirmCancel() {
      this.removeApp = ''
      this.removeAppFormatted = ''
      this.confirmModal = false
    },
    async onIntegrateSlack() {
      if (this.user.isAdmin) {
        const confirmation = confirm(
          'Integrating Managr to your slack workspace will request access to a channel (you can choose a new one or an existing one) we will post a message letting the members of that channel know they can now integrate their Slack accounts',
        )
        if (!confirmation) {
          return
        }
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
            return res
          }
        }
      } else {
        // if (!this.hasSlackIntegration) {
        try {
          let res = await SlackOAuth.api.getOAuthLink(SlackOAuth.options.USER)
          if (res.link) {
            window.location.href = res.link
          }
        } catch (e) {
        } finally {
          this.generatingToken = false
          return res
        }
        // }
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
            this.$toast(
              'We could not retrieve your timezone from zoom, to fix this please login to the zoom.us portal through a browser and return to managr to reintegrate',
              {
                timeout: 2000,
                position: 'top-left',
                type: 'success',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              },
            )
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
    isOnboarding() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.onboarding
    },
    isPaid() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.isPaid
    },
    hasSalesforceIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.salesforceAccount
    },
    hasHubspotIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.hubspotAccount
    },
    hasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.slackRef
    },
    hasZoomIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.zoomAccount && this.$store.state.user.hasZoomIntegration
    },
    hasGongIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.gongAccount && this.$store.state.user.hasGongIntegration
    },
    hasOutreachIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return (
        !!this.$store.state.user.outreachAccount && this.$store.state.user.hasOutreachIntegration
      )
    },
    hasSalesloftIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return (
        !!this.$store.state.user.salesloftAccount && this.$store.state.user.hasSalesloftIntegration
      )
    },
    orgHasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.slackIntegration
    },
    hasSlackIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.slackRef
    },
    hasNylasIntegration() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.nylas
    },
    userCanIntegrateSlack() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.isAdmin
    },
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
    selectedIntegrationSwitcher() {
      switch (this.selectedIntegration) {
        case 'SALESFORCE':
          return Salesforce
        case 'HUBSPOT':
          return Hubspot
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
        case 'OUTREACH':
          return OutreachAccount
        default:
          return null
      }
    },
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
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
@import '@/styles/modals';

.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
  filter: invert(40%);
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}
.right-tooltip {
  position: relative;
  display: inline-block;
}

.right-tooltip .right-tooltiptext {
  visibility: hidden;
  width: 150px;
  background-color: $base-gray;
  opacity: 0.9;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  position: absolute;
  z-index: 1;
  top: -2px;
  left: 115%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.right-tooltip:hover .right-tooltiptext {
  visibility: visible;
}

a {
  text-decoration: none;
  color: white !important;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.img-border {
  @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 6px;
  margin-right: 8px;
}
// .filter-dot {
//   height: 0.4rem;
//   filter: invert(80%);
//   margin-left: 0.5rem;
//   filter: invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg) brightness(93%) contrast(89%);
// }
.filter-loft {
  filter: brightness(0%) invert(7%) sepia(31%) saturate(2639%) hue-rotate(115deg) brightness(92%)
    contrast(91%);
}
.integrations {
  color: $base-gray;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0px 0px 0px 96px;
  &__cards {
    display: flex;
    flex-direction: row;
    padding: 0.5rem 1.5rem;
    flex-wrap: wrap;
    justify-content: flex-start;
    width: 96vw;
    margin-top: 4px;
  }
}
// .gold-filter {
//   filter: invert(81%) sepia(35%) saturate(920%) hue-rotate(343deg) brightness(91%) contrast(90%);
//   margin-left: 4px;
// }
.space-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 116%;
}
// .card:hover {
//   transform: scale(1.015);
//   box-shadow: 1px 2px 2px $very-light-gray;
// }
.card {
  background-color: $white;
  padding: 16px 24px;
  border: 1px solid #e8e8e8;
  margin-right: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: row;
  width: 420px;
  min-height: 144px;
  transition: all 0.25s;

  &__header {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px 16px;
    border-radius: 6px;

    img {
      padding: 0;
      margin: 0;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 12px;
    h3 {
      margin: 0;
      padding: 0;
    }
    p {
      font-size: 12px;
    }
  }
}
.lb-bg {
  background-color: $very-light-blue;
  border: 1px solid $very-light-blue;
}
.vlb-bg {
  background: rgb(181, 222, 255);
  background: linear-gradient(90deg, rgba(181, 222, 255, 1) 1%, rgba(127, 196, 251, 1) 100%);
  border: 1px solid $very-light-blue;
}
.og-bg {
  background: rgb(233, 233, 233);
  background: linear-gradient(90deg, rgba(233, 233, 233, 1) 1%, rgb(227, 231, 235) 100%);
  border: 1px solid rgba(233, 233, 233, 1);
}
.lg-bg {
  background: rgb(140, 255, 191);
  background: linear-gradient(90deg, rgba(140, 255, 191, 1) 1%, rgba(106, 198, 146, 1) 90%);
  border: 1px solid $white-green;
}
.lr-bg {
  background: rgb(251, 165, 192);
  background: linear-gradient(90deg, rgba(251, 165, 192, 1) 1%, rgba(247, 109, 152, 1) 100%);
  border: 1px solid $light-red;
}
.lbp-bg {
  background: rgb(147, 162, 247);
  background: linear-gradient(90deg, rgb(181, 191, 244) 0%, rgb(176, 185, 245) 32%);
  border: 1px solid $very-light-blue;

  //   background: rgb(238,174,202);
  // background: radial-gradient(circle, rgba(238,174,202,1) 0%, rgba(148,187,233,1) 100%);
}
.lp-bg {
  background: rgb(221, 184, 255);
  background: linear-gradient(90deg, rgba(221, 184, 255, 1) 1%, rgba(193, 122, 255, 1) 97%);
  border: 1px solid $light-purple;
}
.vlp-bg {
  background: rgb(197, 194, 255);
  background: linear-gradient(90deg, rgba(197, 194, 255, 1) 1%, rgba(145, 139, 255, 1) 97%);
  border: 1px solid $light-purple;
}
.lo-bg {
  background: rgb(255, 197, 158);
  background: linear-gradient(90deg, rgba(255, 197, 158, 1) 1%, rgba(255, 156, 89, 1) 78%);
  border: 1px solid $light-orange;
}
.required {
  filter: invert(50%) sepia(100%) saturate(901%) hue-rotate(323deg) brightness(110%) contrast(96%);
  margin-left: 4px;
}
.card-text {
  font-size: 14px;
  color: $light-gray-blue;
  text-align: center;
}
// .privacy {
//   color: $base-gray;
//   font-size: 12px;
// }
// .lock {
//   height: 1rem;
// }
a {
  text-decoration: none;
  color: $grape;
  font-weight: bold;
}
.inactive {
  color: $light-gray-blue;
  padding: 4px 8px;
}
.welcome {
  margin-top: -4px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100vw;
  margin-left: 88px;
  padding: 0px 4px;
  overflow: hidden;
  h3 {
    font-size: 19px;
    font-weight: 500;
    margin-left: 28px;
    color: $light-gray-blue;
    letter-spacing: 0.7px;
  }

  p {
    font-size: 14px;
    letter-spacing: 0.1px;
  }
  div {
    display: flex;
    flex-direction: row;
    align-items: center;

    // p {
    //   margin-right: 16px;
    // }
  }
}
.orange_button {
  @include gray-text-button();
  color: $dark-green;
  padding: 6px 12px;
  font-size: 11px;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.invite-form {
  @include small-modal();
  min-width: 37vw;
  // min-height: 64vh;
  align-items: center;
  justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
// .modal-form {
//   width: 100%;
//   background-color: $white;
//   height: 40vh;
//   // justify-content: space-evenly;
// }
.confirm-form {
  // width: 37vw;
  height: 24vh;
}
.form-margin-small {
  margin-top: 10rem;
}
.header {
  // background-color: $soft-gray;
  width: 100%;
  // border-bottom: 1px solid $soft-gray;
  position: relative;
  border-top-right-radius: 4px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 4px;
  // display: flex;
  // flex-direction: row;
  // align-items: center;
  // justify-content: flex-start;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $base-gray;
  }
}
.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-self: start;
  margin: 0 5%;
  letter-spacing: 1px;
}
.flex-row-wrapper {
  display: flex;
  justify-content: space-between;
}
.logo {
  height: 24px;
  margin-left: 0.25rem;
  margin-right: 0.5rem;
  filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
    brightness(93%) contrast(89%);
}
.invite-button {
  @include primary-button();
  // margin-top: 2.5rem;
  margin-bottom: 1rem;
  width: 15vw;
  font-size: 16px;
}
.modal-button {
  @include primary-button();
  // box-shadow: none;
  margin-top: 1rem;
  // height: 2.5rem;
  // width: 19rem;
}

// Tooltip
.side-wrapper {
  display: flex;
  flex-direction: row;
}
.side-wrapper .side-icon {
  position: relative;
  // background: #FFFFFF;
  border-radius: 50%;
  padding: 12px;
  // margin: 20px 12px 0px 10px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  // outline: 1px solid $mid-gray;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip {
  display: block;
  width: 180px;
  height: auto;
  position: absolute;
  // top: -10px; // for double line
  top: -5px; // for single line
  left: 30px;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  bottom: 40%;
  left: 0%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.side-wrapper .side-icon:hover .side-tooltip {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.side-wrapper .side-icon:hover span,
.side-wrapper .side-icon:hover .side-tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}
.side-wrapper .side-workflow:hover,
.side-wrapper .side-workflow:hover .side-tooltip,
.side-wrapper .side-workflow:hover .side-tooltip::before {
  // margin-top: 1rem;
  background: $grape;
  color: #ffffff;
}
.side-icon:hover {
  transition: all 0.1s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  // transition: all .3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  img {
    filter: invert(90%);
  }
}
</style>
