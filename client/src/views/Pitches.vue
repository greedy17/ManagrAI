<template>
  <div ref="pitchTop" class="pitch-view">
    <!-- paidModal -->
    <Modal v-if="paidModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closePaidModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Upgrade to Pro</h3>
              <h5 class="regen-body-title">
                You have reached your usage limit for the month. Please upgrade your plan.
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="instructions" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div class="cancel-button" @click="closePaidModal">Close</div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>
    <!-- resetModal -->
    <Modal v-if="resetModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closeResetModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Are you sure?</h3>
              <h5 class="regen-body-title">This writing style will be permanently removed.</h5>
            </div>
            <!-- <textarea v-autoresize v-model="instructions" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div class="cancel-button" @click="closeResetModal">Cancel</div>
            <div class="reset-button mar-left gray-border" @click="resetWritingStyle">Delete</div>
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="inputModalOpen" class="paid-modal">
      <div
        :style="isMobile ? 'width: 95%; min-height: 275px' : 'width: 610px; min-height: 275px'"
        class="regen-container"
      >
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Learn Writing Style</h4>
            <p class="regen-header-subtitle">
              Provide a sample of the writing style you want to emulate
            </p>
          </div>
          <div v-if="!savingStyle" class="pointer" @click="toggleLearnInputModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div class="paid-body">
          <input
            style="width: 600px"
            class="input-text"
            placeholder="Name your writing style..."
            type="text"
            v-model="styleName"
            :disabled="savingStyle"
          />
          <div class="sample-row">
            <div style="width: 604px" class="input-container">
              <div class="input-row relative">
                <textarea
                  :disabled="savingStyle"
                  maxlength="8000"
                  class="area-input text-area-input"
                  style="padding: 16px 0 0 0"
                  placeholder="Paste sample here..."
                  v-model="sample"
                  v-autoresize
                />

                <div class="absolute-count">
                  <small>{{ remainingStyleChars }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div class="input-row">
            <button :disabled="savingStyle" @click="toggleLearnInputModal" class="secondary-button">
              Cancel
            </button>
            <button :disabled="savingStyle" @click="saveWritingStyle" class="primary-button">
              {{ savingStyle ? 'Learning' : 'Learn' }}
              <div style="margin-left: 4px" v-if="savingStyle" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="journalistModalOpen" class="paid-modal" style="z-index: 1000000">
      <div style="min-height: 275px; width: 510px" class="regen-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">
              {{ !journalists ? 'Find Journalists/Influencers' : 'Journalists/Influencers' }}
            </h3>
            <p class="regen-header-subtitle">
              {{ !journalists ? 'Provide additional details below' : 'Journalist details' }}
            </p>
          </div>
          <div v-if="!loadingJournalists" class="pointer" @click="toggleJournalistModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div
          :class="loadingJournalists ? 'opaque' : ''"
          v-if="!journalists"
          class="paid-body input-width"
        >
          <label for="pub">Publication Type</label>
          <input
            class="input-text"
            placeholder="(e.g., Tier 1, industry-specific, niche, TikTok influencers, etc.)"
            type="text"
            v-model="pubType"
            :disabled="loadingJournalists"
            id="pub"
          />

          <label for="beat">Beat</label>
          <input
            class="input-text"
            placeholder="(e.g., Technology, health, lifestyle, etc.)"
            type="text"
            v-model="beat"
            :disabled="loadingJournalists"
            id="beat"
          />

          <label for="loc">Location</label>
          <input
            class="input-text"
            placeholder="(e.g., National, Atlanta, D.C, etc.)"
            type="text"
            v-model="location"
            :disabled="loadingJournalists"
            id="loc"
          />
        </div>

        <div v-else class="paid-body">
          <pre v-html="journalists" class="pre-text" style="font-size: 14px"></pre>
        </div>

        <div class="paid-footer align-right">
          <div class="input-row">
            <button
              :disabled="loadingJournalists"
              @click="toggleJournalistModal"
              class="secondary-button"
            >
              {{ !journalists ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!journalists"
              @mouseenter="changeJournalText"
              @mouseleave="defaultJournalText"
              :disabled="loadingJournalists || !isPaid"
              @click="getJournalists"
              class="primary-button no-transitions"
            >
              {{ journalText }}
              <div style="margin-left: 4px" v-if="loadingJournalists" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button v-else @click="copyJournalText" class="primary-button no-transitions">
              {{ copyTip }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="feedbackModalOpen" class="paid-modal" style="z-index: 1000000s">
      <div style="min-height: 275px; width: 510px" class="regen-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">
              {{
                !feedback
                  ? 'Optimize Content'
                  : regeneratedFeedback && feedback
                  ? 'Optimized Content'
                  : 'Optimize Content'
              }}
            </h3>
            <p class="regen-header-subtitle">
              {{
                !feedback
                  ? 'Get content feedback by providing additional details'
                  : regeneratedFeedback && feedback
                  ? 'Below is the revised version'
                  : 'Get content feedback by providing additional detail'
              }}
            </p>
          </div>
          <div v-if="!loadingFeedback" class="pointer" @click="toggleFeedbackModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div
          :class="loadingFeedback ? 'opaque' : ''"
          v-if="!feedback"
          class="paid-body input-width"
        >
          <label for="pt">Post Type</label>
          <input
            class="input-text"
            placeholder="(e.g., blog post, LinkedIn post, Tweet, Instagram, email, etc.)"
            type="text"
            v-model="feedbackType"
            :disabled="loadingFeedback"
            id="pt"
          />

          <label for="aud">Audience</label>
          <input
            class="input-text"
            placeholder="(e.g., age range, profession, interests, etc.)"
            type="text"
            v-model="audience"
            :disabled="loadingFeedback"
            id="aud"
          />

          <label for="po">Post Objective</label>
          <input
            class="input-text"
            placeholder="(e.g., to inform, to persuade, to entertain, etc.)"
            type="text"
            v-model="objective"
            :disabled="loadingFeedback"
            id="po"
          />

          <label for="sf">Specific feedback</label>
          <input
            class="input-text"
            placeholder="(e.g., headline effectiveness, clarity, engagement tactics, etc.)"
            type="text"
            v-model="specificFeedback"
            :disabled="loadingFeedback"
            id="sf"
          />
        </div>

        <div v-else class="paid-body">
          <pre v-html="feedback" class="pre-text" style="font-size: 14px"></pre>
        </div>

        <div class="paid-footer align-right">
          <div class="input-row">
            <button
              :disabled="loadingFeedback"
              @click="toggleFeedbackModal"
              class="secondary-button"
            >
              {{ !feedback ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!feedback"
              @mouseenter="changeFeedbackText"
              @mouseleave="defaultFeedbackText"
              :disabled="loadingFeedback || !isPaid"
              @click="getFeedback"
              class="primary-button no-transitions"
            >
              {{ feedbackText }}
              <div style="margin-left: 4px" v-if="loadingFeedback" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button
              :disabled="loadingFeedback || !isPaid"
              v-else-if="feedback && !regeneratedFeedback"
              @click="handleRegenerateFeedback"
              class="primary-button no-transitions"
            >
              Apply Feedback
              <div style="margin-left: 4px" v-if="loadingFeedback" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>

            <button v-else @click="copyFeedbackText" class="primary-button no-transitions">
              {{ copyTip }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="saveModalOpen" class="paid-modal" style="z-index: 1000000">
      <div
        :style="isMobile ? 'width: 95%; min-height: 275px' : 'width: 510px; min-height: 275px'"
        class="regen-container"
      >
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">Save</h3>
            <p class="regen-header-subtitle">Save your pitch</p>
          </div>
          <div v-if="!savingPitch" class="pointer" @click="toggleSaveModal">
            <small>X</small>
          </div>
          <div v-else><small>X</small></div>
        </div>
        <div :class="savingPitch ? 'opaque' : ''" class="paid-body input-width">
          <label for="pub">Pitch Name:</label>
          <input
            class="input-text"
            placeholder="Name your pitch"
            type="text"
            v-model="pitchName"
            :disabled="savingPitch"
            id="pub"
          />
        </div>

        <div class="paid-footer align-right">
          <div class="input-row">
            <button :disabled="savingPitch" @click="toggleSaveModal" class="secondary-button">
              Cancel
            </button>
            <button
              :disabled="savingPitch"
              @click="createSavedPitch"
              class="primary-button no-transitions"
            >
              Save
              <div style="margin-left: 4px" v-if="savingPitch" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <section class="container">
      <div class="content-body">
        <div>
          <!-- <div class="row-start">
            <div style="cursor: text" class="image-container-blue right-margin-m">
              <img
                class="blue-filter"
                style="margin-left: -1px"
                src="@/assets/images/logo.png"
                height="16px"
                alt=""
              />
            </div>
            <h3>Managr</h3>
          </div> -->

          <div style="margin-top: -4px" class="small-container">
            <p style="margin: 0; font-size: 16px" class="bold">Create content</p>
            <p style="margin: 0">
              Choose type (media pitch, blog post, etc.), provide key data, and select a writing
              style.
            </p>
          </div>
        </div>

        <div class="small-container" style="width: 100%; margin-top: 1rem">
          <div
            style="
              padding-top: 1rem;
              padding-bottom: 128px;
              overflow-y: scroll;
              height: 100%;
              border-top: 1px solid rgba(0, 0, 0, 0.1);
            "
          >
            <div style="position: relative">
              <label for="content-type">Content Type</label>
              <input
                class="primary-input"
                type="text"
                name="content-type"
                v-model="type"
                :disabled="loading"
                maxlength="300"
                placeholder="(e.g., create a 200 word media pitch, draft a blog post, etc.)"
                id=""
              />
              <div class="absolute-count">
                <small>{{ remainingCharsSample }}</small>
              </div>
            </div>

            <div style="position: relative">
              <label for="key-data">Key Data</label>
              <textarea
                style="margin-top: 1rem"
                class="area-input-bordered"
                id="key-data"
                placeholder="Paste relevant data, a news summary, or notes."
                v-model="output"
                :rows="3"
                v-autoresize
                :disabled="loading"
                maxlength="5000"
              />

              <div style="bottom: -2px" class="absolute-count">
                <small>{{ remainingChars }}</small>
              </div>
            </div>

            <label style="margin-top: 1rem" for="writing-style">Writing Style</label>
            <div style="margin-top: 1rem; width: 100%; position: relative" id="writing-style">
              <div
                @click="toggleStyleDropdown"
                class="drop-text pointer"
                :class="loading ? 'textcursor' : ''"
              >
                <p class="ellipsis-text" style="margin: 0">
                  {{ writingStyleTitle ? writingStyleTitle : 'Select Style' }}
                </p>
                <img
                  v-if="!showStyleDropdown"
                  src="@/assets/images/downArrow.svg"
                  class="inverted"
                  height="14px"
                  alt=""
                />
                <img
                  class="rotate-img inverted"
                  v-else
                  src="@/assets/images/downArrow.svg"
                  height="14px"
                  alt=""
                />
              </div>

              <div v-if="showStyleDropdown" class="content-dropdown">
                <div class="drop-container">
                  <section v-if="userWritingStyles.length">
                    <p
                      style="
                        margin-bottom: 0;
                        padding-bottom: 8px;
                        cursor: text;
                        color: #2f4656;
                        font-size: 16px;
                        position: sticky;
                        top: 0;
                        background-color: white;
                        z-index: 15;
                      "
                    >
                      Styles
                    </p>
                    <div
                      @click="addWritingStyle(style.style, style.title)"
                      class="dropdown-item"
                      style="padding: 4px 0"
                      v-for="(style, i) in defaultWritingStyles"
                      :key="i"
                    >
                      <p style="padding: 0 16px; margin: 0">{{ style.title }}</p>
                    </div>
                    <div class="divider"></div>
                    <div
                      @mouseenter="setIndex(i)"
                      @mouseLeave="removeIndex"
                      @click="addWritingStyle(style.style, style.title)"
                      class="dropdown-item"
                      v-for="(style, i) in userWritingStyles"
                      :key="i"
                      style="padding: 4px 0"
                    >
                      <p style="padding: 0 16px; margin: 0">
                        {{ style.title }}
                      </p>

                      <div @click="openResetModal(style.id)" class="absolute-icon">
                        <img
                          v-if="hoverIndex === i"
                          src="@/assets/images/trash.svg"
                          height="12px"
                          alt=""
                        />
                      </div>
                    </div>

                    <div style="padding: 8px 0; position: sticky; bottom: 0; background: white">
                      <button
                        @mouseenter="changeStyleText"
                        @mouseleave="defaultStyleText"
                        style="margin-bottom: 8px; width: 86%"
                        @click="toggleLearnInputModal"
                        class="primary-button"
                      >
                        {{ styleText }}
                      </button>
                    </div>
                  </section>
                  <section style="padding: 8px 0" v-else>
                    <p
                      style="
                        margin-bottom: 0;
                        padding-bottom: 8px;
                        cursor: text;
                        color: #2f4656;
                        font-size: 16px;
                        position: sticky;
                        top: 0;
                        background-color: white;
                        z-index: 15;
                      "
                    >
                      Styles
                    </p>

                    <div
                      @click="addWritingStyle(style.style, style.title)"
                      class="dropdown-item"
                      style="padding: 4px 0"
                      v-for="(style, i) in defaultWritingStyles"
                      :key="i"
                    >
                      <p style="padding: 0 16px; margin: 0">{{ style.title }}</p>
                    </div>

                    <button
                      @mouseenter="changeStyleText"
                      @mouseleave="defaultStyleText"
                      style="margin-top: 8px"
                      @click="toggleLearnInputModal"
                      class="primary-button"
                    >
                      {{ styleText }}
                    </button>
                  </section>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer sticky-bottom">
        <div style="padding-bottom: 8px" class="flex-end small-container">
          <!-- <div
            :class="{ fadedimg: !storedType && !storedOutput && !storedWritingStyle }"
            @click="refillContent"
            class="wrapper image-container"
          >
            <img
              style="margin-bottom: 2px"
              src="@/assets/images/refresh-pr.svg"
              height="14px"
              alt=""
            />
            <div class="tooltip">Refill form</div>
          </div> -->

          <div class="rows">
            <button @click="clearForm" :disabled="loading" class="secondary-button">Clear</button>
            <button
              @click="generatePitch"
              :disabled="!type || !writingStyle || loading"
              class="primary-button"
            >
              Generate
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="container gray-bg">
      <div class="header sticky-top gray-bg" v-if="pitch">
        <div class="space-between margin-top-s horizontal-padding">
          <p class="sub-text">{{ pitch.split(' ').length }} words</p>

          <div class="rows">
            <div
              @click="toggleFeedbackModal"
              class="wrapper icon-button white-bg"
              :class="{ 'bluee-bg': feedback }"
              style="margin-right: 0.5rem"
            >
              <img
                style="cursor: pointer"
                class="right-mar img-highlight"
                src="@/assets/images/thumb.svg"
                height="14px"
                alt=""
              />
              <div class="tooltip-below">
                {{ !feedback ? 'Optimize Content' : 'View Feedback' }}
              </div>
            </div>

            <div
              @click="toggleJournalistModal"
              class="wrapper icon-button white-bg"
              :class="{ 'bluee-bg': journalists }"
              style="margin-right: 0.5rem"
            >
              <img
                style="cursor: pointer"
                class="right-mar img-highlight"
                src="@/assets/images/profile.svg"
                height="14px"
                alt=""
              />
              <div class="tooltip-below">
                {{ !journalists ? 'Find Journalists' : 'View Journalists' }}
              </div>
            </div>

            <div
              style="margin-right: 0.5rem"
              @click="copyText"
              class="wrapper icon-button white-bg"
            >
              <img
                style="cursor: pointer"
                class="right-mar img-highlight"
                src="@/assets/images/clipboard.svg"
                height="14px"
                alt=""
              />
              <div class="tooltip-below">{{ copyTip }}</div>
            </div>

            <div>
              <button
                @click="toggleSaveModal"
                class="green-button"
                :disabled="savingPitch || pitchSaved"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>

      <div
        style="margin-top: -2rem"
        v-if="!pitch && !loading"
        class="content-body centered-content"
      >
        <div class="centered-col">
          <div style="cursor: text" class="image-container white-bg extra-padding">
            <img src="@/assets/images/comment.svg" height="32px" alt="" />
          </div>
          <p>Your content will appear here.</p>
        </div>
      </div>

      <div v-else-if="loading" class="content-body centered-content">
        <div class="loading">
          <p>Generating content</p>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>

      <div style="margin-top: 0.5rem" v-else-if="pitch" class="content-body">
        <div class="small-container">
          <pre class="pre-text" v-html="pitch"></pre>
        </div>
      </div>

      <div class="footer sticky-bottom gray-bg">
        <div class="input-container-alt">
          <img class="left-margin-l" src="@/assets/images/pencil.svg" height="14px" alt="" />

          <textarea
            class="area-input-alt text-area-input"
            :placeholder="!pitch ? 'Start by generating content...' : 'Make edits...'"
            autocomplete="off"
            :disabled="!pitch"
            @keyup.enter="regeneratePitch"
            v-autoresize
            v-model="instructions"
          />
          <div
            style="cursor: text; margin-left: 1.5rem"
            v-if="!pitch"
            class="image-container white-bg wrapper"
          >
            <img src="@/assets/images/paper-plane-top.svg" height="14px" alt="" />
            <div class="tooltip">Submit</div>
          </div>

          <div
            style="margin-left: 1.5rem"
            @click="regeneratePitch"
            class="image-container white-bg wrapper"
            v-else
          >
            <img
              style="margin: 0"
              src="@/assets/images/paper-plane-full.svg"
              height="14px"
              alt=""
              class="filtered-blue"
            />
            <div class="tooltip">Submit</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users/'

export default {
  name: 'Pitches',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      defaultWritingStyles: [
        {
          title: 'Default',
          style: `Begin with a precise introduction, without informal salutations. Be clear, concise, and informative, avoiding metaphors. Offer coherent data without persuasion. Aim for depth, not sensationalism and avoid commercial bias.`,
        },
        {
          title: 'Media Pitch',
          style: `Author's Style Guidelines:
0. Start email with "Hi {Journalist first name}", end with "Thanks,". Get right to it, no opening fluff like "I hope this message finds you well"
1. Tone: Maintain a professional, respectful tone. Show appreciation for the journalist's work and express interest in collaboration.
2. Formality: Use formal language, but avoid jargon. Keep sentences clear and concise.
3. Structure: Start with a personalized greeting. Follow with a brief appreciation of the journalist's work, then introduce your topic. Provide key insights, then propose collaboration. End with a forward-looking statement and a thank you.
4. Linguistic Idiosyncrasies: Use active voice and precise, impactful words. Include statistics and expert opinions for credibility.
5. Credibility: Establish credibility by referencing recent research, expert opinions, and relevant industry trends.
6. Engagement: Engage the reader by offering exclusive insights and proposing collaboration.
7. Non-Promotional: Avoid promotional language. Focus on providing valuable, informative content.
8. Stylistic Techniques: Use a mix of short and long sentences for rhythm. Use rhetorical questions to engage the reader and provoke thought.`,
        },
        {
          title: 'Blog Post',
          style: `The author's style is formal and informative, using a journalistic tone to convey complex scientific concepts in a digestible manner. The structure is linear, starting with historical context and leading to the current developments. The author uses technical jargon, but also provides explanations to ensure understanding. Credibility is established through the mention of renowned scientists, historical achievements, and the university's long-standing involvement in the field. The author avoids persuasive language, focusing on facts and achievements.
Guidelines: Maintain a formal, journalistic tone. Use technical terms but provide explanations. Structure content linearly, starting with historical context. Establish credibility through mention of renowned figures and achievements. Avoid persuasive language, focusing on facts.`,
        },
        {
          title: 'Email',
          style: `1. Start with a friendly greeting: Use 'Hey' or 'Hi' to initiate a warm, approachable tone.
2. Be direct and concise: Avoid fluff and unnecessary details. Get straight to the point.
3. Maintain a neutral tone: Avoid persuasive or sales-oriented language. The tone should be informative, not promotional.
4. Use simple, clear language: Avoid jargon or complex terms. The goal is to be understood by all readers.
5. Structure: Use short sentences and paragraphs. Break up information into digestible chunks.
6. Credibility: Use facts and data to support points. Avoid personal opinions or assumptions.
7. Action point: End with a clear, actionable step for the reader. This should be direct and easy to understand.
8. Informality: Maintain a casual, friendly tone throughout. This helps to engage the reader and make the content more relatable.
9. Linguistic idiosyncrasies: Use common, everyday language. Avoid overly formal or academic language.
10. Objectivity: Maintain an unbiased stance. Avoid taking sides or expressing personal views.`,
        },
      ],
      defaultStyle: {},
      regeneratedFeedback: false,
      feedbackModalOpen: false,
      saveModalOpen: false,
      loadingJournalists: false,
      loadingFeedback: false,
      journalists: null,
      location: null,
      beat: null,
      pubType: null,
      feedbackType: null,
      audience: null,
      objective: null,
      specificFeedback: null,
      feedback: null,
      feedbackText: 'Submit',
      journalText: 'Search',
      journalistModalOpen: false,
      contentLoading: false,
      showStyleDropdown: false,
      styleName: null,
      hoverIndex: null,
      styleText: 'Learn writing style',
      deleteId: null,
      inputModalOpen: false,
      showBanner: false,
      writingStyleTitle: null,
      type: '',
      output: '',
      savedOutput: '',
      persona: '',
      briefing: '',
      characters: null,
      pitch: null,
      loading: false,
      regenerating: false,
      paidModal: false,
      showingTypeDropdown: false,
      showingAudienceDropdown: false,
      showingCharacterDropdown: false,
      showingInstructionsDropdown: false,
      storedEvent: null,
      storedPlaceholder: '',
      optionalPlaceholder: 'Optional',
      instructionsPlaceholder: 'What would you like written?',
      typeSuggestions: [
        `Press Release`,
        `Media Pitch`,
        `Blog Post`,
        `LinkedIn Post`,
        `Twitter Post`,
        `Email`,
      ],
      audienceSuggestions: [
        `Millenial moms`,
        `Vegans`,
        `College students`,
        `Local writers in Georgia`,
        `Gen Z`,
        `Health and wellness enthusiast`,
      ],
      characterSuggestions: [`250`, `500`, `750`, `1000`, `1500`],
      instructionsSuggestions: [
        `Create a media pitch for XXX about ...`,
        `Write a LinkedIn Post about XXX`,
        `Issue a press release on behalf of XXX about ...`,
        // `Use the text below to generate XXX for XXX ...`,
        `Re-write the content below using my writing style:`,
        `Tweak this content slightly, enhance readability:`,
      ],
      instructions: '',
      copyTip: 'Copy',
      textToCopy: '',
      showSaveName: false,
      savingPitch: false,
      pitchName: '',
      savedPitch: null,
      showUpdateBanner: false,
      showInput: false,
      sample: '',
      savingStyle: false,
      writingStyle: null,
      resetModal: false,
      storedOutput: null,
      storedWritingStyle: null,
      storedType: null,
      storedWritingStyleTitle: null,
    }
  },
  watch: {
    currentPitch(newVal, oldVal) {
      if (newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setPitch(newVal)
      }
    },
  },
  beforeDestroy() {
    this.$store.commit('setGeneratedContent', null)
  },
  methods: {
    clearForm() {
      // this.storeContent()
      this.output = ''
      this.writingStyle = null
      this.writingStyleTitle = null
      this.type = ''
    },
    storeContent() {
      this.storedOutput = this.output
      this.storedWritingStyle = this.writingStyle
      this.storedType = this.type
      this.storedWritingStyleTitle = this.writingStyleTitle
    },
    refillContent() {
      if (!this.storedOutput && !this.storedWritingStyle && !this.storedType) {
        return
      } else {
        this.output = this.storedOutput
        this.writingStyle = this.storedWritingStyle
        this.type = this.storedType
        this.writingStyleTitle = this.storedWritingStyleTitle
      }
    },
    toggleSaveModal() {
      this.saveModalOpen = !this.saveModalOpen
    },
    async getJournalists() {
      this.loadingJournalists = true
      try {
        await Comms.api
          .getJournalists({
            type: this.pubType,
            beat: this.beat,
            location: this.location,
            content: this.pitch,
          })
          .then((response) => {
            this.journalists = response.journalists
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingJournalists = false
      }
    },
    async getFeedback() {
      this.loadingFeedback = true
      try {
        await Comms.api
          .getFeedback({
            type: this.feedbackType,
            audience: this.audience,
            objective: this.objective,
            feedback: this.specificFeedback,
            content: this.pitch,
          })
          .then((response) => {
            console.log(response)
            this.feedback = response.feedback
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingFeedback = false
      }
    },
    async handleRegenerateFeedback() {
      this.loadingFeedback = true
      try {
        await Comms.api
          .regenerateWithFeedback({
            content: this.pitch,
            feedback: this.feedback,
          })
          .then((response) => {
            console.log(response)
            this.regeneratedFeedback = true
            this.feedback = response.feedback
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingFeedback = false
      }
    },
    toggleJournalistModal() {
      this.journalistModalOpen = !this.journalistModalOpen
    },
    toggleFeedbackModal() {
      this.feedbackModalOpen = !this.feedbackModalOpen
    },
    enforceMax() {
      if (this.characters > 1500) {
        this.characters = 1500
      }
    },
    toggleStyleDropdown() {
      if (!this.loading) {
        this.showStyleDropdown = !this.showStyleDropdown
      } else {
        return
      }
    },
    test() {
      console.log(this.userWritingStyles)
    },
    setIndex(i) {
      this.hoverIndex = i
    },
    removeIndex() {
      this.hoverIndex = null
    },
    async saveWritingStyle() {
      this.savingStyle = true
      try {
        await Comms.api
          .saveWritingStyle({
            example: this.sample,
            title: this.styleName,
          })
          .then((response) => {
            this.$toast('Writing style saved', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.sample = ''
        this.styleName = ''
        this.toggleLearnInput()
        this.savingStyle = false
        this.refreshUser()
        this.toggleLearnInputModal()
      }
    },
    async resetWritingStyle() {
      this.savingStyle = true
      this.sample = ''
      this.writingStyleTitle = ''
      this.closeResetModal()
      try {
        await Comms.api.deleteWritingStyle({ style_id: this.deleteId })
        this.toggleLearnInput()
      } catch (e) {
        console.log(e)
      } finally {
        this.savingStyle = false
        this.deleteId = null
        this.writingStyle = null
        this.refreshUser()
      }
    },

    changeFeedbackText() {
      if (!this.isPaid) {
        this.feedbackText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultFeedbackText() {
      if (!this.isPaid) {
        this.feedbackText = 'Submit'
      } else {
        return
      }
    },

    changeJournalText() {
      if (!this.isPaid) {
        this.journalText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultJournalText() {
      if (!this.isPaid) {
        this.journalText = 'Search'
      } else {
        return
      }
    },

    changeStyleText() {
      if (!this.isPaid) {
        this.styleText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultStyleText() {
      if (!this.isPaid) {
        this.styleText = 'Learn writing style'
      } else {
        return
      }
    },
    openResetModal(id) {
      this.resetModal = true
      this.deleteId = id

      if (this.showStyleDropdown === true) {
        this.showStyleDropdown = false
      }
    },
    closeResetModal() {
      this.resetModal = false
    },
    toggleLearnInput() {
      if (this.isPaid) {
        this.showInput = !this.showInput
      }
    },
    toggleLearnInputModal() {
      if (this.isPaid) {
        this.inputModalOpen = !this.inputModalOpen

        if (this.showStyleDropdown === true) {
          this.showStyleDropdown = false
        }
      }
    },
    async copyText() {
      try {
        await navigator.clipboard.writeText(this.pitch)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyJournalText() {
      try {
        await navigator.clipboard.writeText(this.journalists)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyFeedbackText() {
      try {
        await navigator.clipboard.writeText(this.feedback)
        this.copyTip = 'Copied!'
        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    resetSearch() {
      this.pitch = null
      this.writingStyle = ''
      this.writingStyleTitle = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.instructions = ''
    },
    showTypeDropdown() {
      this.showingTypeDropdown = true
    },
    hideTypeDropdown() {
      this.showingTypeDropdown = false
    },
    showAudienceDropdown() {
      this.showingAudienceDropdown = true
    },
    hideAudienceDropdown() {
      this.showingAudienceDropdown = false
    },
    showCharacterDropdown(e) {
      // this.storedEvent = e
      // this.storedPlaceholder = e.target.placeholder
      // e.target.placeholder = ''
      this.optionalPlaceholder = ''
      this.showingCharacterDropdown = true
    },
    hideCharacterDropdown() {
      this.optionalPlaceholder = 'Optional'
      // this.storedEvent.target.placeholder = this.storedPlaceholder
      // this.storedPlaceholder = ''
      this.showingCharacterDropdown = false
    },
    showInstructionsDropdown(e) {
      // this.storedEvent = e
      // this.storedPlaceholder = e.target.placeholder
      // e.target.placeholder = ''
      this.instructionsPlaceholder = ''
      this.showingInstructionsDropdown = true
    },
    hideInstructionsDropdown() {
      // this.storedEvent.target.placeholder = this.storedPlaceholder
      // this.storedPlaceholder = ''
      this.instructionsPlaceholder = 'What would you like written?'
      this.showingInstructionsDropdown = false
    },
    addWritingStyle(ex, title) {
      this.writingStyle = ex
      this.writingStyleTitle = title
      this.showStyleDropdown = false
      this.hideTypeDropdown()
    },
    addAudienceSuggestion(ex) {
      this.persona = ex
      this.hideAudienceDropdown()
    },
    addCharacterSuggestion(ex) {
      this.characters = ex
      this.hideCharacterDropdown()
    },
    addInstructionsSuggestion(ex) {
      this.output = ex
      this.hideInstructionsDropdown()
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.pitchTop.scrollIntoView({ behavior: 'smooth' })
      }, 450)
    },
    openPaidModal() {
      this.paidModal = true
    },
    closePaidModal() {
      this.paidModal = false
    },
    goToContact() {
      window.open('https://managr.ai/contact', '_blank')
    },
    toggleRegenerate() {
      this.regenerating = !this.regenerating
    },
    async createSavedPitch() {
      this.showSaveName = false
      this.savingPitch = true
      try {
        const response = await Comms.api.savePitch({
          name: this.pitchName || this.pitch.slice(0, 60),
          user: this.user.id,
          type: this.type,
          audience: this.persona,
          generated_pitch: this.pitch,
          instructions: this.output,
        })
        if (response.id) {
          // this.searchId = response.id

          this.savedPitch = {
            name: response.name,
            user: this.user.id,
            type: this.type,
            audience: this.persona,
            generated_pitch: this.pitch,
            instructions: this.output,
          }

          this.$toast('Content saved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })

          await this.$store.dispatch('getPitches')
        }
      } catch (e) {
        console.log(e)
      } finally {
        // this.showUpdateBanner = true

        setTimeout(() => {
          this.saveModalOpen = false
          this.savingPitch = false
          this.successToggle()
        }, 2000)
      }
    },
    successToggle() {
      this.showUpdateBanner = true
      setTimeout(() => {
        this.showUpdateBanner = false
      }, 2000)
    },
    async regeneratePitch() {
      this.regenerating = false
      this.contentLoading = true
      this.loading = true
      const tempPitch = this.pitch
      this.pitch = null
      this.savedOutput = this.instructions
      try {
        await Comms.api
          .regeneratePitch({
            pitch: tempPitch,
            instructions: this.instructions,
          })
          .then((response) => {
            this.pitch = response.pitch
          })
      } catch (e) {
        console.log('ERROR CREATING PITCH::', e)
      } finally {
        // this.clearData()
        this.instructions = ''
        this.contentLoading = false
        this.loading = false
        this.scrollToTop()
      }
    },
    async generatePitch() {
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal()
        return
      }
      this.storeContent()
      this.pitch = null
      this.feedback = null
      this.specificFeedback = null
      this.feedbackType = null
      this.audience = null
      this.objective = null
      this.regeneratedFeedback = false
      this.journalists = null
      this.loading = true
      this.showStyleDropdown = false
      console.log(
        this.type + ' --- ENDS HERE ---',
        this.output + '--- ENDS HERE ---',
        this.writingStyle + '--- ENDS HERE---',
      )
      try {
        await Comms.api
          .generatePitch({
            type: this.type,
            instructions: this.output,
            style: this.writingStyle,
          })
          .then((response) => {
            // this.clearForm()
            this.savedOutput = this.output
            this.pitch = response.pitch
            this.scrollToTop()
            this.$store.commit('setGeneratedContent', null)
          })
          .then((response) => {
            this.refreshUser()
          })
          .then((response) => {
            this.$store.dispatch('getPitches')
          })
      } catch (e) {
        console.log('ERROR CREATING PITCH', e)
      } finally {
        // this.clearData()
        this.loading = false
        this.scrollToTop()
      }
    },
    setPitch(pitch) {
      this.pitch = pitch.generated_pitch
      this.type = pitch.type
      this.output = pitch.instructions
      this.persona = pitch.audience

      // this.generatePitch()
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          // do nothing for now
          return null
        })
    },
    clearData() {
      this.type = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.sample = ''
      this.writingStyle = ''
    },
  },
  computed: {
    userWritingStyles() {
      return this.$store.state.user.writingStylesRef
    },
    remainingChars() {
      return 5000 - this.output.length
    },
    remainingCharsBrief() {
      return 2000 - this.briefing.length
    },
    remainingCharsSample() {
      return 300 - this.type.length
    },
    remainingStyleChars() {
      return 8000 - this.sample.length
    },
    isMobile() {
      return window.innerWidth <= 600
    },
    user() {
      return this.$store.state.user
    },
    filteredTypeSuggestions() {
      if (!this.type) return this.typeSuggestions
      return this.typeSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.type.toLowerCase()),
      )
    },
    filteredAudienceSuggestions() {
      if (!this.persona) return this.audienceSuggestions
      return this.audienceSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.persona.toLowerCase()),
      )
    },
    filteredCharacterSuggestions() {
      if (!this.characters) return this.characterSuggestions
      return this.characterSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.characters.toLowerCase()),
      )
    },
    filteredInstructionsSuggestions() {
      if (!this.output) return this.instructionsSuggestions
      return this.instructionsSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.output.toLowerCase()),
      )
    },
    isPaid() {
      return !!this.$store.state.user.organizationRef.isPaid
    },
    searchesUsed() {
      let arr = []
      let currentMonth = new Date(Date.now()).getMonth() + 1
      if (currentMonth < 10) {
        currentMonth = `0${currentMonth}`
      } else {
        currentMonth = `${currentMonth}`
      }
      let currentYear = new Date(Date.now()).getFullYear()
      for (let key in this.$store.state.user.metaData) {
        const item = this.$store.state.user.metaData[key]
        const filteredByMonth = item.timestamps.filter((date) => {
          const split = date.split('-')
          return split[1] == currentMonth && split[0] == currentYear
        })
        arr = [...arr, ...filteredByMonth]
      }
      return arr.length
    },
    currentPitch() {
      return this.$store.state.currentPitch
    },
    pitchSaved() {
      if (this.savedPitch && this.pitch && this.savedPitch.generated_pitch === this.pitch) {
        return true
      } else if (
        this.pitch &&
        this.currentPitch &&
        this.currentPitch.generated_pitch === this.pitch
      ) {
        return true
      } else {
        return false
      }
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
    clickOutsideInstructionsMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideInstructionsDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsideTypeMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideTypeDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsideAudienceMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideAudienceDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsideCharacterMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideCharacterDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.green-button {
  @include dark-blue-button();
  background-color: $dark-green;
  padding: 8px 16px;
  border: none;
  margin-right: 0;
}

.icon-button {
  @include dark-blue-button();
  padding: 7px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  img {
    filter: invert(40%);
  }
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

.margin-top-s {
  margin-top: 1.5rem;
}

.padding-top-l {
  padding-top: 88px;
}

.header {
  padding: 60px 16px 8px 16px;
  width: 100%;
  background-color: white;
  z-index: 2;
}

.extra-padding {
  padding: 12px !important;
}

.sticky-top {
  position: absolute;
  top: 0;
}

.centered-col {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 14px;
  width: 100%;
  height: 80%;
}

.area-input-alt {
  width: 85%;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.25;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}

label {
  font-size: 14px;
  font-weight: bold !important;
}

.sticky-bottom {
  position: absolute;
  bottom: 0;
}

.footer {
  padding: 16px 40px 32px 40px;
  width: 100%;
  background-color: white;
  z-index: 10;
}

.content-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  overflow-y: scroll;
  scroll-behavior: smooth;
  z-index: 0;
  padding: 88px 40px 32px 40px;
  font-size: 16px;
  width: 100%;
  height: 100%;
}

.content-body::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.content-body::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.horizonal-padding {
  padding-left: 32px;
  padding-right: 32px;
}

.bold {
  font-family: $base-font-family;
  font-weight: 200 !important;
}

h3 {
  font-size: 20px;
  margin: 0;
}

.small-container {
  padding-left: 32px;
  padding-right: 32px;
  font-size: 15px;
  line-height: 1.75;
}

.horizontal-padding {
  padding-left: 56px;
  padding-right: 64px;
}

.spacer {
  padding-top: 68px;
}
.space-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

p,
label {
  @media only screen and (max-width: 600px) {
    font-size: 14px !important;
  }
}

.container {
  width: 50vw;
  height: 100vh;
  position: relative;

  @media only screen and (max-width: 600px) {
    width: 100vw;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 100vw;
  }
}

.container:first-of-type {
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}

.image-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
}

.image-container-blue {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: $dark-black-blue;

  img {
    filter: brightness(0) invert(100%);
  }
}

.sticky-bottom {
  position: absolute;
  bottom: 0;
}

.left-margin {
  margin-left: 8px;
}
.left-margin-m {
  margin-left: 12px;
}

.left-margin-l {
  margin-left: 16px;
}

.right-margin {
  margin-right: 8px;
}
.right-margin-m {
  margin-right: 12px;
}

.bottom-margin-xl {
  margin-bottom: 32px;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.title-container {
  position: relative;
  display: flex;
  justify-content: space-between;
  width: 100%;
  @media only screen and (max-width: 600px) {
    margin-top: 1rem;
  }
}

.relative {
  position: relative;
}

.absolute-count {
  position: absolute;
  bottom: 0;
  right: 3px;
  font-size: 10px;
  color: $light-gray-blue;
  // background-color: $white-blue;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  // border-radius: 4px;
  // padding: 2px 4px;
}

.no-text-margin {
  margin: 0;
}

.centered-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
}

// .sub-text {
//   color: $light-gray-blue;
//   margin: 8px 0 16px 0;
//   font-size: 14px;

//   font-family: $thin-font-family;
//   span {
//     font-weight: normal;
//     word-wrap: break-word;
//   }
// }

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0;
  font-size: 14px;
  font-family: $thin-font-family;

  span {
    font-weight: 200;
    word-wrap: break-word;
  }
  // @media only screen and (max-width: 600px) {
  //   text-align: center;
  // }
}

.title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-top: 1rem;
}

.row-start {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-left: -10px;
}
.rows {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  text-align: start !important;

  button:first-of-type {
    margin-right: 1rem;
  }
}

.pitch-container {
  padding: 16px 0 2px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  @media only screen and (max-width: 600px) {
    // width: 80%;
  }
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;

  margin-right: 8px;
}

.pre-text {
  // background-color: $white-blue;
  padding: 40px 0 88px 0;
  border-radius: 4px;
  // padding: 16px;
  margin: 0;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.dark-blue-bg {
  background-color: $dark-black-blue;
  padding: 23px 0 30px;
}

.pitch-view {
  font-family: $thin-font-family;
  font-size: 14px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  background-color: white;
  color: $dark-black-blue;

  @media only screen and (max-width: 600px) {
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    /* Styles for tablets */
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  // height: 100%;
  padding-top: 32px;
  font-size: 14px;
  color: $dark-black-blue;
  gap: 24px;
  @media only screen and (max-width: 600px) {
    padding-top: 4px;
  }
}

.input-container-alt {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Horizontal offset, vertical offset, blur radius, color */
  transition: box-shadow 0.3s ease;
  padding: 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  flex-direction: row;

  img {
    filter: invert(40%);
  }
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 1rem;
  margin-top: 0.95rem;
  border-radius: 6px;
  // width: 675px;
  width: 100%;
  min-height: 4.9rem;
  background-color: $offer-white;
  color: $base-gray;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
.input-container-chat {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem;
  border-radius: 6px;
  width: 50%;
  background-color: $offer-white;
  color: $base-gray;
  position: relative;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}

.number-input {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: $offer-white;
  padding: 6px 2px;
  outline: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family;
  font-weight: 400;
  margin-top: 8px;
  border-radius: 4px;
  width: 80px;
}

.number-input::placeholder {
  font-size: 11px;
}

.area-input-bordered {
  border-radius: 6px;
  width: 100%;
  background-color: white;
  margin-bottom: 0.25rem;
  max-height: 200px;
  padding: 1rem 1.25rem;
  line-height: 1.75;
  outline: none;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family;
  font-weight: 400;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input {
  width: 85%;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.25;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}

.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input:disabled,
.area-input-bordered:disabled {
  cursor: not-allowed;
}

.area-input::-webkit-scrollbar,
.area-input-bordered::-webkit-scrollbar {
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb,
.area-input-bordered::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.regen-input {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 6px;
  width: 400px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 8px 1rem;
  font-family: $base-font-family;
  @media only screen and (max-width: 600px) {
    // position: static;
    width: 23%;
  }
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}
.main-text {
  width: 132px;
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1rem;
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    margin-right: 8px;
    filter: invert(40%);
  }
}

.drop-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin: 0;
  font-size: 14px;
  color: $dark-black-blue;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 12px 16px;
  svg,
  img {
    margin-left: 4px;
    filter: invert(40%);
  }
}

.drop-text:hover {
  opacity: 0.7;
}

footer {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-bottom: 1rem;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  white-space: nowrap;
  margin-left: 1rem;

  img {
    margin-right: 0.5rem;
  }
}

.extra-padding {
  padding: 12px 8px;
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.primary-input {
  width: 100%;
  margin: 1rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 13px;
  padding: 16px 20px 16px 18px;
  outline: none;
}

.input-text {
  width: 600px;
  margin: 1rem 0;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family !important;
  background-color: $offer-white;
  font-size: 13px;
  padding: 10px 20px 10px 18px;
  outline: none;
}

.input-width {
  input {
    width: 500px !important;
    @media only screen and (max-width: 600px) {
      width: 95% !important;
    }
  }
}

.reset-button {
  @include white-button-danger();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  margin-right: -2px;
}

.mar-left {
  margin-left: 1rem;
}

.blue-bg {
  padding: 16px 0;
  background-color: $white-blue;
}

.opaque {
  opacity: 0.75;
}

.img-highlight {
  filter: invert(40%);

  &:hover {
    filter: none;
  }
}

.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip,
.wrapper .tooltip-wide {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.wrapper .tooltip-below {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  top: 150%;
  color: #fff;
  display: block;
  left: -30px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.tooltip-wide {
  width: 150px !important;
  left: -60px !important;
}

.wrapper .tooltip:before,
.wrapper .tooltip-wide:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip-below:before {
  top: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after,
.wrapper .tooltip-wide:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper .tooltip-below:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-bottom: solid $dark-black-blue 10px;
  top: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip,
.wrapper:hover .tooltip-wide,
.wrapper:hover .tooltip-below {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip,
.lte8 .wrapper .tooltip-wide,
.lt38 .wrapper .tooltip-below {
  display: none;
}

.lte8 .wrapper:hover .tooltip,
.lte8 .wrapper:hover .tooltip-wide,
.lte8 .wrapper:hover .tooltip-below {
  display: block;
}
.save-wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.save-wrapper .save-tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: 15px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 130px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the save-tooltip without it disappearing */
.save-wrapper .save-tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.save-wrapper .save-tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.save-wrapper:hover .save-tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .save-wrapper .save-tooltip {
  display: none;
}

.lte8 .save-wrapper:hover .save-tooltip {
  display: block;
}

.back {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0.75rem;
  left: -56px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 3px 2px;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
  @media only screen and (max-width: 600px) {
    // position: static;
    width: 1.5rem;
    left: 50%;
    top: -2rem;
    // margin-bottom: 1rem;
  }
}

.summary-load-text {
  font-family: $thin-font-family;
  font-size: 14px;
}

.summary-preview-skeleton {
  width: 100%;
  // min-width: 400px;
  padding: 8px 0;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  @media only screen and (max-width: 600px) {
    width: 80%;
  }
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  display: inline-block;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
}

.meta-wide {
  width: 100%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shorter {
  width: 80%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shortest {
  width: 60%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.extra-margin-top {
  // margin-top: 16px;
  margin-top: 5.5rem;
  @media only screen and (max-width: 600px) {
    margin-top: 0rem;
  }
}
.paid-modal {
  margin-top: 132px;
  @media only screen and (max-width: 600px) {
    margin-top: 62px;
  }
}
.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  color: $base-gray;
  font-family: $thin-font-family;

  label {
    font-size: 14px;
  }
  @media only screen and (max-width: 600px) {
    width: 95%;
  }
}
.paid-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  position: sticky;
  top: 0;
  background-color: white;
}
.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.regen-header-title {
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 12px;
  color: $light-gray-blue;
  margin: 0.5rem 0;
}
.pointer {
  cursor: pointer;
}
.textcursor {
  cursor: text !important;
}
.paid-body {
  margin: 0.5rem 0;
  scroll-behavior: smooth;
  overflow-y: scroll;
}
.regen-body-title {
  margin: 0 0 0 0;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
}
.align-right {
  justify-content: flex-end !important;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  padding-bottom: 8px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.gray-border {
  border: 1px solid $soft-gray;
}
.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
.dropdown {
  padding: 8px 0 16px 0;
  position: relative;
  height: fit-content;
  max-height: 232px;
  width: 100%;
  top: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  display: none;
}
.dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.dropdown:hover::-webkit-scrollbar,
.content-dropdown:hover::-webkit-scrollbar {
  display: block;
}

.paid-body::-webkit-scrollbar,
.content-dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.paid-body::-webkit-scrollbar-thumb,
.content-dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.paid-body:hover::-webkit-scrollbar {
  display: block;
}

.dropdown-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 8px;
  width: 100%;
  min-height: 100px;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  z-index: 2300;

  p {
    margin: 0;
  }
}

.ellipsis-text {
  max-width: 400px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.dropdown-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  padding: 8px 0;
  width: 100%;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 14px;
  // z-index: 2300;

  p {
    margin: 0;
    padding: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}

.absolute-icon {
  position: absolute;
  padding-left: 4px;
  background: transparent;
  background-color: white;
  // opacity: 0;
  right: 0;
  cursor: pointer;

  img {
    &:hover {
      filter: invert(66%) sepia(47%) saturate(6468%) hue-rotate(322deg) brightness(85%)
        contrast(96%);
    }
  }
}

.gray-text {
  color: $mid-gray;
}
.mar-top {
  margin-top: 1rem;
}
.text-area-input::placeholder {
  // padding-top: 1rem;
}
.text-area-input {
  padding-top: 1.25rem;
}
.divider {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  margin-left: 8px !important;
  margin-top: 4px;
  margin-bottom: 4px;
}

.divider-text {
  position: absolute;
  top: -24px;
  left: 44%;
  z-index: 20;
  background-color: white;
  padding: 4px 16px;
  border-radius: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  @media only screen and (max-width: 600px) {
    left: 39%;
  }
}
.content {
  // width: 80%;
}

input::placeholder,
textarea::placeholder {
  font-family: $thin-font-family !important;
  color: $light-gray-blue;
}

.area-input-outline {
  width: 300px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  padding: 5px 8px;
  border-radius: 4px;
  line-height: 1.75;
  border: 1px solid rgba(0, 0, 0, 0.1);
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  margin-right: 1rem;
  resize: none;
}
.no-mar {
  margin: 0;
}
.primary-button:disabled {
  background-color: $soft-gray;
}

.no-transitions:hover {
  scale: 1 !important;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  cursor: not-allowed !important;
  opacity: 0.7;
}
.circle-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 100%;
  padding: 5px 6px;
  background-color: $white-blue;
  img {
    margin: 0 !important;
  }
}
.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}
.templates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 8px;
  left: 45%;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 2000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.invert {
  filter: invert(96%);
}

.sample-row {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.img-margin {
  img {
    margin: 0 4px;
  }
}

.thin-font {
  font-family: $thin-font-family;
}

.green-filter {
  filter: invert(66%) sepia(20%) saturate(1059%) hue-rotate(101deg) brightness(89%) contrast(93%);
}

.faded {
  filter: invert(55%);
}

.fadedimg {
  filter: opacity(40%);
  cursor: text;
}

.gray-bg {
  background-color: $off-white;
}

.rotate-img {
  transform: rotate(180deg);
}

.content-dropdown {
  width: 60%;
  overflow-y: scroll;
  max-height: 400px;
  position: absolute;
  bottom: 60px;
  left: 0;
  font-size: 13px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 3;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    padding: 8px 16px;
    color: #7c7b7b;
    cursor: pointer;
    width: 245px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.grow:hover {
  transform: scale(1.2);
  box-shadow: 2px 4px 32px rgba($color: $black, $alpha: 0.3);
  opacity: 0.7;
}
.grow {
  transition: all 0.2s;
}
.loading {
  display: flex;
  // justify-content: center;
  align-items: center;
  border-radius: 6px;
  // padding: 1.5rem 0.75rem;
  padding: 1.5rem 0;
}
.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
.white-bg {
  background: white;
}
.bluee-bg {
  background: $white-blue !important;
  img {
    filter: invert(50%);
  }
}
.absolute-right {
  position: absolute;
  right: 8px;
  top: -48px;
}
.text-truncation {
  width: 60%;
  white-space: nowrap;
  overflow-x: hidden;
  text-overflow: ellipsis;
}
.main-text-img {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  filter: invert(40%);
  margin: 0;
  padding-right: 1rem;
}
.cancel-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $offer-white;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 6px;
  cursor: pointer;
  // box-shadow: 1px 1px 3px 1px rgba(0, 0, 0, 0.1);
  margin: 12px 0;

  img {
    transform: rotate(45deg);
  }
  transition: all 0.2s;
}
.lip-img {
  height: 14px;
  padding: 0;
  margin: 0;
  z-index: 5500;
}
.invert-dark-blue {
  filter: invert(22%) sepia(51%) saturate(390%) hue-rotate(161deg) brightness(92%) contrast(87%);
}
.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
}
.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
}
.create-report-container {
  width: 50%;
  padding: 0 32px;
  @media only screen and (max-width: 600px) {
    width: 95%;
  }
}
.width-dynamic {
  width: 50%;
  @media only screen and (max-width: 600px) {
    width: 95%;
  }
}
.pitch-padding {
  padding: 0px 48px 16px 56px;
  @media only screen and (max-width: 600px) {
    padding: 0px 32px 16px 32px;
  }
}
</style>