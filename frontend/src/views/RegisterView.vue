<template>
  <AppLayout>
    <section class="register-container">
      <div class="register-card">
        <div v-if="isSelectionPage" class="register-header">
          <h1><i class="fas fa-user-graduate" aria-hidden="true"></i> Placify</h1>
          <p>Join our placement ecosystem as a Student or Company</p>
        </div>
        <div v-else class="register-header">
          <h1><i :class="mode === 'company' ? 'fas fa-building' : 'fas fa-user-graduate'" aria-hidden="true"></i> {{ currentTitle }}</h1>
          <p>Register and start applying for amazing placement opportunities</p>
        </div>

        <div v-if="isSelectionPage" class="choices-container">
          <RouterLink class="choice-card" to="/register/student">
            <span class="choice-icon"><i class="fas fa-graduation-cap" aria-hidden="true"></i></span>
            <div class="choice-content">
              <h3 class="choice-title">Register as Student</h3>
              <p class="choice-description">Find your perfect placement opportunity</p>
              <ul class="features-list">
                <li>Browse placement drives</li>
                <li>Apply to companies</li>
                <li>Track applications</li>
                <li>Build your profile</li>
                <li>Upload resume</li>
              </ul>
            </div>
          </RouterLink>

          <RouterLink class="choice-card" to="/register/company">
            <span class="choice-icon"><i class="fas fa-building" aria-hidden="true"></i></span>
            <div class="choice-content">
              <h3 class="choice-title">Register as Company</h3>
              <p class="choice-description">Connect with talented students</p>
              <ul class="features-list">
                <li>Post job opportunities</li>
                <li>Review applications</li>
                <li>Shortlist candidates</li>
                <li>Manage placements</li>
                <li>View analytics</li>
              </ul>
            </div>
          </RouterLink>
        </div>

        <div v-else class="form-shell">
          <div class="pp-form-alert pp-form-alert-info mb-4">
            <i class="fas fa-info-circle me-2" aria-hidden="true"></i>All fields marked with <span class="required-mark">*</span> are required.
          </div>

          <div v-if="mode === 'student'">
            <form class="needs-validation" novalidate @submit.prevent="handleStudentRegister">
              <div v-if="error" class="alert alert-danger"><i class="fas fa-exclamation-circle me-2" aria-hidden="true"></i>{{ error }}</div>
              <div v-if="success" class="alert alert-success"><i class="fas fa-check-circle me-2" aria-hidden="true"></i>{{ success }}</div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-user" aria-hidden="true"></i>
                  <h3>Personal Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Full Name <span class="required-mark">*</span></label>
                    <input v-model="studentForm.name" class="form-control" placeholder="Enter your full name" required />
                    <small class="field-hint">2-100 characters</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Email Address <span class="required-mark">*</span></label>
                    <input v-model="studentForm.email" type="email" class="form-control" placeholder="your.email@example.com" required />
                    <small class="field-hint">Must be a valid email address</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Phone Number <span class="required-mark">*</span></label>
                    <input v-model="studentForm.phone" type="tel" class="form-control" placeholder="+91-9876543210" required />
                    <small class="field-hint">Minimum 10 digits</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Password <span class="required-mark">*</span></label>
                    <input v-model="studentForm.password" type="password" class="form-control" placeholder="Create a strong password" required minlength="8" />
                    <small class="field-hint">Min 8 chars, uppercase, lowercase, number</small>
                  </div>
                </div>
              </div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-graduation-cap" aria-hidden="true"></i>
                  <h3>Academic Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Enrollment Number <span class="required-mark">*</span></label>
                    <input v-model="studentForm.enrollment_number" class="form-control" placeholder="e.g., ENR2021001" required />
                    <small class="field-hint">2-20 characters, unique</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Department <span class="required-mark">*</span></label>
                    <select v-model="studentForm.department" class="form-select" required>
                      <option value="" disabled>-- Select Department --</option>
                      <option v-for="dept in departmentOptions" :key="dept" :value="dept">{{ dept }}</option>
                    </select>
                    <small class="field-hint">Select your department</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Course <span class="required-mark">*</span></label>
                    <input v-model="studentForm.course" class="form-control" placeholder="e.g., B.Tech, B.Sc" required />
                    <small class="field-hint">e.g., B.Tech, B.Sc, B.E</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Year of Study <span class="required-mark">*</span></label>
                    <select v-model="studentForm.year_of_study" class="form-select" required>
                      <option value="" disabled>-- Select Year --</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                    </select>
                    <small class="field-hint">Select your current year</small>
                  </div>
                </div>
              </div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-briefcase" aria-hidden="true"></i>
                  <h3>Additional Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label">Skills</label>
                    <input v-model="studentForm.skills" class="form-control" placeholder="e.g., Java, Python, Web Development, Data Science" />
                    <small class="field-hint">Comma-separated list of your skills (optional, max 200 characters)</small>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Bio / About You</label>
                    <textarea v-model="studentForm.bio" class="form-control" rows="3" placeholder="Tell us about yourself, your interests, achievements..."></textarea>
                    <small class="field-hint">Optional, maximum 500 characters</small>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Resume Upload</label>
                    <input ref="resumeInput" type="file" class="form-control" accept=".pdf,.doc,.docx" @change="onResumeChange" />
                    <small class="field-hint">PDF, DOC, or DOCX (optional)</small>
                  </div>
                  <div class="col-12">
                    <div class="form-check">
                      <input v-model="studentForm.terms_accepted" class="form-check-input" type="checkbox" id="studentTerms" required />
                      <label class="form-check-label" for="studentTerms">I agree to the <a href="#" @click.prevent>Terms and Conditions</a> and <a href="#" @click.prevent>Privacy Policy</a></label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="btn-container btn-container--submit">
                <button type="submit" class="btn-proceed btn-proceed--full" :disabled="loading">
                  <i class="fas fa-check" aria-hidden="true"></i>{{ loading ? 'Registering...' : 'Register Now' }}
                </button>
              </div>
            </form>
          </div>

          <div v-else>
            <form class="needs-validation" novalidate @submit.prevent="handleCompanyRegister">
              <div v-if="error" class="alert alert-danger"><i class="fas fa-exclamation-circle me-2" aria-hidden="true"></i>{{ error }}</div>
              <div v-if="success" class="alert alert-success"><i class="fas fa-check-circle me-2" aria-hidden="true"></i>{{ success }}</div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-building" aria-hidden="true"></i>
                  <h3>Company Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Full Name <span class="required-mark">*</span></label>
                    <input v-model="companyForm.name" class="form-control" placeholder="Enter your full name" required />
                    <small class="field-hint">2-100 characters</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Email Address <span class="required-mark">*</span></label>
                    <input v-model="companyForm.email" type="email" class="form-control" placeholder="your.email@example.com" required />
                    <small class="field-hint">Must be a valid email address</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Password <span class="required-mark">*</span></label>
                    <input v-model="companyForm.password" type="password" class="form-control" placeholder="Create a strong password" required minlength="8" />
                    <small class="field-hint">Min 8 chars, uppercase, lowercase, number</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Phone Number <span class="required-mark">*</span></label>
                    <input v-model="companyForm.phone" type="tel" class="form-control" placeholder="+91-9876543210" required />
                    <small class="field-hint">Minimum 10 digits</small>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Company Name <span class="required-mark">*</span></label>
                    <input v-model="companyForm.company_name" class="form-control" placeholder="e.g., Acme Technologies Pvt Ltd" required />
                    <small class="field-hint">2-100 characters, unique</small>
                  </div>
                </div>
              </div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-address-card" aria-hidden="true"></i>
                  <h3>Contact Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <label class="form-label">Website</label>
                    <input v-model="companyForm.website" class="form-control" placeholder="https://example.com" />
                    <small class="field-hint">Optional, must start with http:// or https://</small>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">HR Contact</label>
                    <input v-model="companyForm.hr_contact" class="form-control" placeholder="e.g., Jane Doe, HR Manager" />
                    <small class="field-hint">Optional</small>
                  </div>
                </div>
              </div>

              <div class="form-section">
                <div class="section-header">
                  <i class="fas fa-briefcase" aria-hidden="true"></i>
                  <h3>Additional Information</h3>
                  <span class="section-line"></span>
                </div>
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label">Company Bio</label>
                    <textarea v-model="companyForm.bio" class="form-control" rows="3" placeholder="Tell us about your company, culture, and what you're hiring for..."></textarea>
                    <small class="field-hint">Optional, maximum 500 characters</small>
                  </div>
                  <div class="col-12">
                    <div class="form-check">
                      <input v-model="companyForm.terms_accepted" class="form-check-input" type="checkbox" id="companyTerms" required />
                      <label class="form-check-label" for="companyTerms">I agree to the <a href="#" @click.prevent>Terms and Conditions</a> and <a href="#" @click.prevent>Privacy Policy</a></label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="btn-container btn-container--submit">
                <button type="submit" class="btn-proceed btn-proceed--full" :disabled="loading">
                  <i class="fas fa-check" aria-hidden="true"></i>{{ loading ? 'Registering...' : 'Register Now' }}
                </button>
              </div>
            </form>
          </div>

          <div class="login-link">
            <p>Already have an account? <RouterLink to="/login">Login here</RouterLink></p>
          </div>
        </div>
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import http from '../api/http'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const resumeInput = ref(null)
const resumeFile = ref(null)

const departmentOptions = [
  'Computer Science',
  'Electrical Engineering',
  'Mechanical Engineering',
  'Civil Engineering',
  'Biotechnology',
  'Chemical Engineering',
  'Aerospace Engineering',
  'Biomedical Engineering',
  'Materials Engineering',
  'Industrial Engineering',
]

const mode = computed(() => (route.path.endsWith('/company') ? 'company' : 'student'))
const isSelectionPage = computed(() => route.path === '/register' || route.path === '/register/')
const currentTitle = computed(() => (mode.value === 'company' ? 'Company Registration' : 'Student Registration'))

const studentForm = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
  enrollment_number: '',
  department: '',
  course: '',
  year_of_study: '',
  bio: '',
  skills: '',
  terms_accepted: false,
})

const companyForm = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
  company_name: '',
  website: '',
  hr_contact: '',
  bio: '',
  terms_accepted: false,
})

function onResumeChange(event) {
  resumeFile.value = event.target.files?.[0] || null
}

function extractErrors(err, fallback) {
  const response = err?.response?.data
  if (Array.isArray(response?.errors)) {
    return response.errors.join(' ')
  }
  return response?.message || fallback
}

async function handleStudentRegister() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const payload = new FormData()
    Object.entries(studentForm).forEach(([key, value]) => payload.append(key, value))
    if (resumeFile.value) {
      payload.append('resume', resumeFile.value)
    }
    await http.post('/api/v1/auth/register/student', payload, {
      headers: { 'Content-Type': undefined },
    })
    success.value = 'Registration successful. Please sign in.'
    router.push('/login')
  } catch (err) {
    error.value = extractErrors(err, 'Unable to register.')
  } finally {
    loading.value = false
  }
}

async function handleCompanyRegister() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await http.post('/api/v1/auth/register/company', {
      ...companyForm,
      terms_accepted: companyForm.terms_accepted,
    })
    success.value = 'Registration successful. Please sign in.'
    router.push('/login')
  } catch (err) {
    error.value = extractErrors(err, 'Unable to register.')
  } finally {
    loading.value = false
  }
}
</script>

<style src="../styles/pages/public/register.css"></style>
<style scoped>
.form-shell {
  margin-top: 1rem;
}

.register-header h1 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.register-header h1 i {
  font-size: 0.9em;
}

.required-mark {
  color: #dc3545;
}

.form-section {
  margin-top: 1.35rem;
  padding-top: 1rem;
  border-top: 1px solid #e6eaf2;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.section-header i {
  color: #00498d;
  font-size: 1.1rem;
}

.section-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #00264d;
}

.section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #00498d, transparent);
}

.field-hint {
  display: block;
  margin-top: 0.35rem;
  color: #8a94a6;
  font-size: 0.8rem;
}

.form-shell :deep(.form-label) {
  font-weight: 600;
  color: #00264d;
  margin-bottom: 0.35rem;
}

.form-shell :deep(.form-control),
.form-shell :deep(.form-select) {
  border: 1px solid #d9e2ee;
  border-radius: 10px;
  background: #f8f9fb;
  padding: 0.65rem 0.9rem;
  box-shadow: none;
}

.form-shell :deep(.form-control:focus),
.form-shell :deep(.form-select:focus) {
  border-color: #00498d;
  box-shadow: 0 0 0 3px rgba(0, 73, 141, 0.12);
  background: #ffffff;
}

.form-shell :deep(textarea.form-control) {
  min-height: 100px;
}

.form-shell :deep(.form-check-label a) {
  color: #00498d;
  font-weight: 600;
  text-decoration: none;
}

.form-shell :deep(.form-check-label a:hover) {
  text-decoration: underline;
}

.btn-container--submit {
  margin-top: 2rem;
}

.btn-proceed--full {
  flex: 1;
  max-width: none;
  width: 100%;
  padding: 16px 30px;
}
</style>
